from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class StudentRegistrationForm(forms.ModelForm):
    # Şifre alanlarına belli bir sınır ekledik.Güvenlik açısından iyi bir geliştirme
    password = forms.CharField(widget=forms.PasswordInput, label="Şifre" , max_length=50)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Şifre Tekrar" , max_length=50)
    full_name = forms.CharField(label="Ad Soyad", help_text="Örn: Ömer Faruk Coşkun" , max_length=50)
    phone = forms.CharField(label="Telefon", max_length=15)

    class Meta:
        model = User
        fields = ['email'] # Kullanıcıdan sadece bunları model için alacağız

    # 1. E-POSTA FİLTRESİ (Domain Kontrolü)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # E-posta zaten var mı kontrolü
        if User.objects.filter(email=email).exists():
            raise ValidationError("Bu e-posta adresi zaten kayıtlı.")

        # Okul e-postası kontrolü
        if not email.endswith('@ogr.iuc.edu.tr'):
            raise ValidationError("Sadece '@ogr.iuc.edu.tr' uzantılı okul e-postası ile kayıt olabilirsiniz.")
        
        return email

    # 2. ŞİFRE EŞLEŞTİRME VE TELEFON KONTROLÜ
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        phone = cleaned_data.get("phone")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Şifreler eşleşmiyor.")

        # Basit telefon kontrolü (Sadece rakam olsun)
        if phone and not phone.isdigit():
             self.add_error('phone', "Telefon numarası sadece rakamlardan oluşmalıdır.")
             
        return cleaned_data

    # 3. VERİTABANI KAYDI (İsim Soyisim Ayrıştırma)
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Kullanıcı adını email yapalım (zorunlu alan olduğu için)
        user.username = user.email 
        user.set_password(self.cleaned_data["password"])

        # Ad Soyad Ayrıştırma Mantığı (Önceki sorundaki düzeltme)
        full_name = self.cleaned_data["full_name"].strip()
        if " " in full_name:
            # Son boşluktan böl: "Ömer Faruk" | "Coşkun"
            first, last = full_name.rsplit(" ", 1)
            user.first_name = first
            user.last_name = last
        else:
            user.first_name = full_name
            user.last_name = ""

        if commit:
            user.save()
        return user