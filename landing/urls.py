from django.urls import path
from . import views

urlpatterns = [
    # Anasayfa
    path('', views.home_view, name='home'),

    # Arkadaşının eklediği Auth sayfası
    path('auth/', views.auth_page_view, name='auth_page'), 

    # --- SİLİNEN KURTARICI SATIRLAR (Bunları geri ekliyoruz) ---
    # HTML 'register' dediğinde buraya gelsin:
    path('kayit-ol/', views.auth_page_view, name='register'),

    # HTML 'login' dediğinde buraya gelsin:
    path('giris-yap/', views.auth_page_view, name='login'),
    # -----------------------------------------------------------

    path('tercihler/', views.preferences_view, name='preferences'),

    # API Endpoints (Eren'in ekledikleri)
    path('api/auth/resend-code', views.api_resend_code, name='api_resend'),
    path('api/auth/send-verification', views.api_register, name='api_register'),
    path('api/auth/verify-code', views.api_verify_code, name='api_verify'),
    path('api/auth/login', views.api_login, name='api_login'),
]