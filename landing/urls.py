from django.urls import path
from . import views

urlpatterns = [
    # --- Sayfalar ---
    path('', views.home_view, name='home'),
    
    # Mevcut auth sayfası
    path('auth/', views.auth_page_view, name='auth_page'), 
    
    # --- EKLENEN KURTARICI SATIRLAR (Hata bunlardan dolayı çıkıyor) ---
    # HTML dosyası 'register' ismini aradığında da aynı sayfayı açsın:
    path('kayit-ol/', views.auth_page_view, name='register'),
    
    # HTML dosyası 'login' ismini aradığında da aynı sayfayı açsın:
    path('giris-yap/', views.auth_page_view, name='login'),
    # ------------------------------------------------------------------

    path('tercihler/', views.preferences_view, name='preferences'),

    # --- API Endpoints ---
    path('api/auth/resend-code', views.api_resend_code, name='api_resend'),
    path('api/auth/send-verification', views.api_register, name='api_register'),
    path('api/auth/verify-code', views.api_verify_code, name='api_verify'),
    path('api/auth/login', views.api_login, name='api_login'),
]