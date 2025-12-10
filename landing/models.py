from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import random



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Otomatik olarak 10 dakika sonra expire olacak şekilde ayarla
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_code():
        """6 haneli rastgele kod üret"""
        return str(random.randint(100000, 999999))
    
    def is_expired(self):
        """Kodun süresi dolmuş mu?"""
        return timezone.now() > self.expires_at
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'E-posta Doğrulama'
        verbose_name_plural = 'E-posta Doğrulamaları'
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    selected_hobbies = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
   
    def __str__(self):
        return f"{self.user.username} Tercihleri"
    
    class Meta:
        verbose_name = 'Kullanıcı Tercihi'
        verbose_name_plural = 'Kullanıcı Tercihleri'
