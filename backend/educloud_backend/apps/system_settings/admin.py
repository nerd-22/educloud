from django.contrib import admin
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['system_name', 'system_email', 'default_language', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Platform Configuration', {
            'fields': (
                'system_name', 'system_email', 'smtp_host', 'smtp_port',
                'smtp_username', 'smtp_password', 'smtp_encryption',
            ),
        }),
        ('Global Defaults', {
            'fields': (
                'default_language', 'default_timezone', 'default_date_format',
                'default_time_format', 'default_currency',
            ),
        }),
        ('Security Settings', {
            'fields': (
                'min_password_length', 'password_requires_special',
                'password_requires_number', 'password_requires_uppercase',
                'session_timeout', 'max_login_attempts', 'lockout_duration',
            ),
        }),
        ('Notification Settings', {
            'fields': (
                'email_notifications', 'system_notifications',
                'maintenance_notifications', 'security_notifications',
            ),
        }),
        ('Integration Settings', {
            'fields': (
                'google_api_key', 'enable_google_login', 'enable_microsoft_login',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance of SystemSettings
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the settings instance
        return False
