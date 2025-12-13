import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt 
from .forms import StudentRegistrationForm
from .models import EmailVerification, Profile, UserPreference
from django.contrib import messages
import random







# ---------------------------------------------------------
# YARDIMCI FONKSİYONLAR
# ---------------------------------------------------------
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# ---------------------------------------------------------
# SAYFA VIEW'LARI (HTML Döner)
# ---------------------------------------------------------

def home_view(request):
    kullanici_sayisi = User.objects.count()
    return render(request, 'landing/home.html', {'total_users': kullanici_sayisi})

def auth_page_view(request):
    """Sadece HTML sayfasını ekrana basar, mantık API'de döner"""
    if request.user.is_authenticated:
        return redirect('preferences')
    return render(request, 'landing/auth.html')

@login_required(login_url='auth_page')
def preferences_view(request):
    if request.method == 'POST':
        hobbies_string = request.POST.get('preferences') 
        notes = request.POST.get('additional_notes')

        UserPreference.objects.update_or_create(
            user=request.user,
            defaults={
                'selected_hobbies': hobbies_string,
                'additional_notes': notes
            }
        )
        return redirect('home')
        
    return render(request, 'landing/preferences.html')

# ---------------------------------------------------------
# API VIEW'LARI (JavaScript ile konuşur - JSON Döner)
# ---------------------------------------------------------

@csrf_exempt 
def api_register(request):
    """Kayıt olma ve Kod Gönderme"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Form validasyonunu manuel çağırıyoruz 
            form = StudentRegistrationForm(data)
            
            if form.is_valid():
                # 1. Kullanıcıyı oluştur (Pasif)
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                # Profil oluştur
                phone = form.cleaned_data.get('phone', '')
                Profile.objects.get_or_create(user=user, defaults={'phone': phone})

                # 2. Kod üret ve kaydet
                code = EmailVerification.generate_code()
                EmailVerification.objects.create(
                    user=user,
                    code=code,
                    ip_address=get_client_ip(request)
                )

                # 3. Mail gönder
                subject = 'İÜC Hediyeleşme - Doğrulama Kodunuz'
                message = f'Merhaba {user.first_name},\n\nHesabını doğrulamak için kodun:\n\n{code}\n\nBu kod 10 dakika geçerlidir.'
                
                try:
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
                    return JsonResponse({'success': True, 'message': 'Kod gönderildi'})
                except Exception as e:
                    user.delete()
                    return JsonResponse({'success': False, 'message': f'Mail gönderilemedi: {str(e)}'}, status=500)
            
            else:
                # Form hatalarını topla (İlk hatayı döndür)
                error_msg = next(iter(form.errors.values()))[0]
                return JsonResponse({'success': False, 'message': error_msg}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Geçersiz veri formatı'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Sunucu hatası: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def api_verify_code(request):
    """Doğrulama Kodu Kontrolü"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')

            # Kullanılmamış ve en yeni kodu bul
            verification = EmailVerification.objects.filter(
                user__email=email, 
                is_used=False
            ).order_by('-created_at').first()

            if verification:
                if verification.code == str(code):
                    if verification.is_expired():
                        return JsonResponse({'success': False, 'message': 'Kodun süresi dolmuş.'}, status=400)
                    
                    # BAŞARILI
                    user = verification.user
                    user.is_active = True
                    user.save()
                    
                    verification.is_used = True
                    verification.save()
                    
                    login(request, user) # Oturum aç
                    
                    return JsonResponse({'success': True, 'message': 'Doğrulama başarılı!', 'token': 'session_active'})
                else:
                    return JsonResponse({'success': False, 'message': 'Hatalı kod!'}, status=400)
            else:
                return JsonResponse({'success': False, 'message': 'Doğrulama kaydı bulunamadı.'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def api_resend_code(request):
    """Doğrulama Kodunu Tekrar Gönder"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            user = User.objects.filter(email=email).first()
            if not user:
                return JsonResponse({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)

            if user.is_active:
                return JsonResponse({'success': False, 'message': 'Bu hesap zaten doğrulanmış.'}, status=400)

            code = EmailVerification.generate_code()
            EmailVerification.objects.create(
                user=user,
                code=code,
                ip_address=get_client_ip(request)
            )

            subject = 'İÜC Hediyeleşme - Yeni Doğrulama Kodunuz'
            message = f'Merhaba {user.first_name},\n\n Yeni kodunuz:\n\n{code}\n\n10 dakika geçerlidir.'
            
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
                return JsonResponse({'success': True, 'message': 'Yeni kod gönderildi!'})
            except:
                return JsonResponse({'success': False, 'message': 'Mail gönderilemedi.'}, status=500)

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
            
    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def api_login(request):
    """Giriş Yapma API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user_obj = User.objects.filter(email=email).first()

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    if not user.is_active:
                         return JsonResponse({'success': False, 'message': 'Hesabınız doğrulanmamış.'}, status=401)
                    
                    login(request, user)
                    return JsonResponse({'success': True, 'message': 'Giriş başarılı'})
                else:
                    return JsonResponse({'success': False, 'message': 'Şifre hatalı'}, status=401)
            else:
                return JsonResponse({'success': False, 'message': 'Kullanıcı bulunamadı'}, status=404)

        except Exception as e:
             return JsonResponse({'success': False, 'message': 'Bir hata oluştu'}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

# landing/views.py içine


# ... diğer importların ...

def register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # 1. Kullanıcıyı kaydet (Pasif olarak)
            user = form.save(commit=False)
            user.is_active = False 
            user.save()
            
            # Not: Signal sayesinde Profile zaten oluştu, telefonu oraya kaydetmeye gerek kalmadı
            # çünkü form.save() sırasında formdaki telefon verisi profile gitmiş olabilir
            # ya da manuel ekleyebiliriz (aşağıda)
            if hasattr(user, 'profile'):
                user.profile.phone = form.cleaned_data.get('phone')
                user.profile.save()

            # 2. PROFESYONEL KOD ÜRETİMİ (Arkadaşının modelini kullanıyoruz)
            # Kod üretmek için random kütüphanesine gerek kalmadı, modelde var.
            code = EmailVerification.generate_code()
            
            # Veritabanına kayıt (Süresi ve durumu otomatik ayarlanacak)
            EmailVerification.objects.create(
                user=user,
                code=code
            )

            # 3. Mail Gönder
            subject = 'İÜC Hediyeleşme - Doğrulama Kodunuz'
            message = f'Merhaba {user.first_name},\n\nHesabını doğrulamak için kodun: {code}\n\nBu kod 10 dakika geçerlidir.'
            
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
                print(f"📧 Mail gönderildi: {code}") # Konsolda görelim
            except Exception as e:
                print(f"❌ Mail hatası: {e}")
                messages.error(request, "Mail gönderilemedi, lütfen tekrar deneyin.")
                return redirect('register')

            # 4. Kullanıcıyı hatırlayalım
            request.session['verification_user_id'] = user.id
            
            # Doğrulama sayfasına yönlendir
            return redirect('verify_email') 
            
    else:
        form = StudentRegistrationForm()

    return render(request, 'landing/auth.html', {'form': form})

# views.py (En alta ekle)

from django.contrib.auth import login # Kullanıcıyı otomatik giriş yaptırmak için

def verify_email_view(request):
    # 1. Session'dan kayıt olan kullanıcının ID'sini al
    user_id = request.session.get('verification_user_id')
    
    # Eğer session'da id yoksa (sayfaya izinsiz girmeye çalışıyorsa) login'e at
    if not user_id:
        messages.error(request, "Önce kayıt olmalısınız.")
        return redirect('register')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        code = request.POST.get('code')
        
        # 2. Veritabanında bu kullanıcıya ait, kullanılmamış bu kodu ara
        verification = EmailVerification.objects.filter(
            user=user, 
            code=code, 
            is_used=False
        ).first()

        if verification:
            # 3. Kod bulundu, peki süresi dolmuş mu?
            if not verification.is_expired():
                # --- BAŞARILI SENARYO ---
                
                # A) Kullanıcıyı Aktif Et
                user.is_active = True
                user.save()
                
                # B) Kodu kullanıldı olarak işaretle (Bir daha kullanamasın)
                verification.is_used = True
                verification.save()
                
                # C) Otomatik Giriş Yaptır
                login(request, user)
                
                # D) Session temizliği
                del request.session['verification_user_id']
                
                messages.success(request, "Hesabınız başarıyla doğrulandı! 🎉")
                return redirect('preferences') # Tercihler sayfasına gönder
            
            else:
                messages.error(request, "Bu kodun süresi dolmuş. Lütfen yeni kod isteyin.")
        else:
            messages.error(request, "Girdiğiniz kod hatalı veya geçersiz.")

    return render(request, 'landing/verify.html')




# landing/views.py EN ALTI

from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def debug_mail_view(request):
    # Ayarları güvenli şekilde al (Yoksa 'Tanımlı Değil' döner, hata vermez)
    user = getattr(settings, 'EMAIL_HOST_USER', 'Tanımlı Değil')
    password_durumu = "Var (Gizli)" if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else "YOK! (Env Kontrol Et)"
    host = getattr(settings, 'EMAIL_HOST', 'Tanımlı Değil')
    port = getattr(settings, 'EMAIL_PORT', 'Tanımlı Değil')
    tls = getattr(settings, 'EMAIL_USE_TLS', 'Tanımlı Değil')
    ssl = getattr(settings, 'EMAIL_USE_SSL', 'Tanımlı Değil') # Hatayı burası veriyordu

    info = f"""
    <h1>Mail Debug Ekranı</h1>
    <p><b>User:</b> {user}</p>
    <p><b>Password Durumu:</b> {password_durumu}</p>
    <p><b>Host:</b> {host}</p>
    <p><b>Port:</b> {port}</p>
    <p><b>TLS:</b> {tls}</p>
    <p><b>SSL:</b> {ssl}</p>
    <hr>
    <h3>Gönderim Sonucu:</h3>
    """
    
    # Mail Göndermeyi Dene
    try:
        send_mail(
            subject='Test Basligi - Render',
            message='Bu Render üzerinden gonderilen test mesajidir. Eger bunu okuyorsan sistem calisiyor demektir.',
            from_email=user,
            recipient_list=['omerfarukcoskun@ogr.iuc.edu.tr'], # Kendi mailin
            fail_silently=False,
        )
        result = "<h2 style='color:green'>✅ BAŞARILI! Mail gitti.</h2><p>Lütfen gelen kutunu ve spam klasörünü kontrol et.</p>"
    except Exception as e:
        # Hatayı ekrana detaylı bas
        result = f"""
        <h2 style='color:red'>❌ HATA OLUŞTU</h2>
        <p><b>Hata Mesajı:</b> {e}</p>
        <p><b>Hata Türü:</b> {type(e).__name__}</p>
        <br>
        <h4>Olası Sebepler:</h4>
        <ul>
            <li><b>SMTPAuthenticationError:</b> Şifren yanlıştır. Normal Gmail şifresini değil, <b>Uygulama Şifresini (App Password)</b> kullanmalısın.</li>
            <li><b>TimeoutError:</b> Render sunucusu Gmail'e ulaşamıyor (Nadir olur).</li>
        </ul>
        """

    return HttpResponse(info + result)