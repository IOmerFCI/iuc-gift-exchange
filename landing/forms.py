from django import forms

class SignUpForm(forms.Form):
    fullname = forms.CharField(required=False, widget=forms.TextInput, label='Ad Soyad')
    email = forms.CharField(required=False, widget=forms.TextInput, label='Eposta')  # EmailField kullanılmıyor
    phone = forms.CharField(required=False, widget=forms.TextInput, label='Telefon')
    password = forms.CharField(required=False, widget=forms.PasswordInput, label='Şifre')
    password_confirm = forms.CharField(required=False, widget=forms.PasswordInput, label='Şifre Tekrar')

    # intentional: no extra validators, accept any text