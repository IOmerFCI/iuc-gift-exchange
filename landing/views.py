from django.shortcuts import render


def home(request):
    """Render the landing page."""
    return render(request, 'landing/home.html')


def auth(request):
    """Render the authentication (login/signup) page."""
    return render(request, 'landing/auth.html')
