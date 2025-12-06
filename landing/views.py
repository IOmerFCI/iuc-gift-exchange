import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.template import TemplateDoesNotExist
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
        return render(request, 'landing/home.html')
    except TemplateDoesNotExist:
        return HttpResponse('Ana sayfa (template bulunamadı).')

def preferences(request):
    """Preferences sayfası: landing/preferences.html render eder; template yoksa düz metin döner."""
    try:
        return render(request, 'landing/preferences.html')
    except TemplateDoesNotExist:
        return HttpResponse('Preferences sayfası (template bulunamadı).')