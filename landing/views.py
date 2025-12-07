import uuid
import json
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.template import TemplateDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .forms import SignUpForm
from .models import Profile

def auth(request):
    """Login / Signup handler — signup accepts any input and saves to DB."""
    if request.method == 'POST':
        # detect signup by presence of signup fields (fullname or password_confirm)
        if 'fullname' in request.POST or 'password_confirm' in request.POST:
            form = SignUpForm(request.POST)
            # form.is_valid() only checks requiredness (we set required=False) so always True
            if form.is_valid():
                data = form.cleaned_data
                fullname = (data.get('fullname') or '').strip()
                email = (data.get('email') or '').strip()
                phone = (data.get('phone') or '').strip()
                password = data.get('password') or ''

                # determine username: prefer email, else generate unique username
                base_username = email if email else f"user_{uuid.uuid4().hex[:8]}"
                username = base_username
                # ensure uniqueness
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

                try:
                    # create user object and save password (or unusable)
                    user = User(username=username, email=email)
                    user.first_name = fullname  # full name stored in first_name
                    if password:
                        user.set_password(password)
                    else:
                        user.set_unusable_password()
                    user.save()

                    # ensure profile and save raw phone
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.phone = phone
                    profile.save()

                    # optional: auto-login if password provided
                    if password:
                        auth_user = authenticate(request, username=username, password=password)
                        if auth_user:
                            auth_login(request, auth_user)
                            return redirect('home')

                    # success response (normal flow)
                    return redirect('home')

                except Exception as e:
                    # render template with error message
                    return render(request, 'landing/auth.html', {
                        'signup_errors': [str(e)],
                        'prefill': {'fullname': fullname, 'email': email, 'phone': phone}
                    })

            # fallback (shouldn't happen)
            return render(request, 'landing/auth.html', {'signup_errors': ['Form geçersiz.'], 'prefill': request.POST})

        # login branch unchanged
        else:
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
            return render(request, 'landing/auth.html', {'login_error': 'E-posta veya şifre yanlış.'})

    # GET
    return render(request, 'landing/auth.html')

def home(request):
    """Ana sayfa: landing/home.html render eder; template yoksa düz metin döner."""
    try:
        # Kayıtlı kullanıcı sayısını hesapla
        user_count = User.objects.count()
        return render(request, 'landing/home.html', {'user_count': user_count})
    except TemplateDoesNotExist:
        return HttpResponse('Ana sayfa (template bulunamadı).')

def preferences(request):
    """Preferences sayfası: landing/preferences.html render eder; template yoksa düz metin döner."""
    try:
        return render(request, 'landing/preferences.html')
    except TemplateDoesNotExist:
        return HttpResponse('Preferences sayfası (template bulunamadı).')

@csrf_exempt
def send_verification(request):
    """
    POST JSON { "email": "..." } -> oluşturulan 6 haneli kodu cache'e kaydeder.
    (Gerçek e-posta gönderimi yapılmaz; sadece doğrulama kodu saklanır.)
    """
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        data = {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return JsonResponse({'message': 'email required'}, status=400)
    code = f"{random.randint(0, 999999):06d}"
    cache.set(f"verif:{email}", code, timeout=600)  # 10 dakika
    # debug: kodu dönebiliriz (dev için). Prod: kaldır.
    return JsonResponse({'sent': True, 'code': code})

@csrf_exempt
def verify_code(request):
    """
    POST JSON { "email": "...", "code": "000000" } -> kod eşleşirse User/Profile oluşturur ve token döner.
    """
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        data = {}
    email = (data.get('email') or '').strip().lower()
    code = (data.get('code') or '').strip()
    if not email or not code:
        return JsonResponse({'message': 'email and code required'}, status=400)
    cached = cache.get(f"verif:{email}")
    if not cached or cached != code:
        return JsonResponse({'message': 'invalid code'}, status=400)
    # kod doğru -> kullanıcı oluştur (kısıtlama yok)
    user, created = User.objects.get_or_create(email=email, defaults={'username': email})
    if created:
        # şifre yoksa unusable, istenirse daha sonra set edilebilir
        user.set_unusable_password()
        user.save()
    profile, _ = Profile.objects.get_or_create(user=user)
    # frontend form may have sent phone/name previously; frontend verifies after code;
    # burada phone/name update logic yapılabilir: frontend can call separate endpoint.
    token = uuid.uuid4().hex
    cache.set(f"token:{email}", token, timeout=60*60*24)  # 1 gün
    cache.delete(f"verif:{email}")
    return JsonResponse({'token': token, 'created': created, 'email': email, 'user_id': user.id})

def cerrahpasa_login(request):
    """Render Cerrahpaşa verification login page."""
    try:
        return render(request, 'landing/cerrahpasa_login.html')
    except TemplateDoesNotExist:
        return HttpResponse('Cerrahpaşa giriş sayfası (template bulunamadı).')

def inspect_user(request):
    """
    Debug endpoint: GET ?email=... -> JSON with user and profile if exists.
    Kullanım: /inspect_user/?email=deneme@... 
    """
    email = request.GET.get('email', '').strip().lower()
    if not email:
        return JsonResponse({'error': 'email param missing'}, status=400)
    try:
        u = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse({'found': False})
    profile_data = None
    try:
        p = Profile.objects.get(user=u)
        profile_data = {'phone': p.phone}
    except Profile.DoesNotExist:
        profile_data = None
    return JsonResponse({
        'found': True,
        'user': {'id': u.id, 'username': u.username, 'email': u.email, 'fullname': u.first_name},
        'profile': profile_data
    })