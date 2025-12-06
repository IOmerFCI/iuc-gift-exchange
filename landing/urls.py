from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.auth, name='auth'),
    path('preferences/', views.preferences, name='preferences'),
    path('inspect_user/', views.inspect_user, name='inspect_user'),
    # Cerrahpaşa login page
    path('cerrahpasa-login/', views.cerrahpasa_login, name='cerrahpasa_login'),
    # API endpoints used by the provided frontend
    path('api/auth/send-verification', views.send_verification, name='send_verification'),
    path('api/auth/verify-code', views.verify_code, name='verify_code'),
]
