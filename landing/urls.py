from django.urls import path
from . import views

urlpatterns = [
    # 1. ANASAYFA (127.0.0.1:8000 buraya gelecek)
    # views.home veya views.index diye bir fonksiyonun olduğunu varsayıyorum
    path('', views.home_view, name='home'), 

    # 2. KAYIT EKRANI (Artık burası özel bir linkte duracak)
    path('kayit-ol/', views.register_view, name='register'),

    # 3. GİRİŞ EKRANI (Varsa)
    path('giris-yap/', views.login_view, name='login'),
]