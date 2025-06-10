from rest_framework import serializers
from .models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [
            # Platform Configuration
            'system_name', 'system_email', 'smtp_host', 'smtp_port',
            'smtp_username', 'smtp_password', 'smtp_encryption',
            
            # Global Defaults
            'default_language', 'default_timezone', 'default_date_format',
            'default_time_format', 'default_currency',
            
            # Security Settings
            'min_password_length', 'password_requires_special',
            'password_requires_number', 'password_requires_uppercase',
            'session_timeout', 'max_login_attempts', 'lockout_duration',
            
            # Notification Settings
            'email_notifications', 'system_notifications',
            'maintenance_notifications', 'security_notifications',
            
            # Integration Settings
            'google_api_key', 'enable_google_login', 'enable_microsoft_login',
        ]
        extra_kwargs = {
            'smtp_password': {'write_only': True},
            'google_api_key': {'write_only': True},
        }
