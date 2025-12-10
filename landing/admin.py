from django.contrib import admin
from .models import UserPreference, EmailVerification, Profile


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'selected_hobbies', 'additional_notes')
    search_fields = ('user__username', 'user__email')
    list_filter = ('user__date_joined',)



@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at', 'is_used', 'ip_address')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'user__username', 'code', 'ip_address')
    readonly_fields = ('created_at', 'expires_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Kullanıcı Bilgisi', {
            'fields': ('user',)
        }),
        ('Doğrulama Kodu', {
            'fields': ('code', 'is_used')
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at', 'expires_at')
        }),
        ('Güvenlik', {
            'fields': ('ip_address',)
        }),
    )
    
    def has_add_permission(self, request):
        # Admin panelinden manuel eklemeyi engelle
        return False



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'get_email', 'get_full_name')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('user__is_active', 'user__date_joined')
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'E-posta'
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Ad Soyad'
    
    fieldsets = (
        ('Kullanıcı', {
            'fields': ('user',)
        }),
        ('İletişim', {
            'fields': ('phone',)
        }),
    )