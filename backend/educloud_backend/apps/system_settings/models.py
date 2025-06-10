from django.db import models
from django.core.validators import MinValueValidator


class SystemSettings(models.Model):
    # Platform Configuration
    system_name = models.CharField(max_length=100, default='EduCloud')
    system_email = models.EmailField(max_length=255, blank=True)
    smtp_host = models.CharField(max_length=255, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    smtp_username = models.CharField(max_length=255, blank=True)
    smtp_password = models.CharField(max_length=255, blank=True)
    smtp_encryption = models.CharField(
        max_length=4,
        choices=[('TLS', 'TLS'), ('SSL', 'SSL'), ('NONE', 'None')],
        default='TLS'
    )

    # Global Defaults
    default_language = models.CharField(
        max_length=20,
        choices=[('English', 'English'), ('French', 'French'), ('Spanish', 'Spanish')],
        default='English'
    )
    default_timezone = models.CharField(
        max_length=20,
        choices=[('UTC', 'UTC'), ('GMT', 'GMT'), ('EST', 'EST'), ('PST', 'PST')],
        default='UTC'
    )
    default_date_format = models.CharField(
        max_length=20,
        choices=[
            ('YYYY-MM-DD', 'YYYY-MM-DD'),
            ('MM/DD/YYYY', 'MM/DD/YYYY'),
            ('DD/MM/YYYY', 'DD/MM/YYYY')
        ],
        default='YYYY-MM-DD'
    )
    default_time_format = models.CharField(
        max_length=2,
        choices=[('12', '12-hour'), ('24', '24-hour')],
        default='24'
    )
    default_currency = models.CharField(
        max_length=3,
        choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP')],
        default='USD'
    )

    # Security Settings
    min_password_length = models.IntegerField(
        default=8,
        validators=[MinValueValidator(8)]
    )
    password_requires_special = models.BooleanField(default=True)
    password_requires_number = models.BooleanField(default=True)
    password_requires_uppercase = models.BooleanField(default=True)
    session_timeout = models.IntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        help_text='Session timeout in minutes'
    )
    max_login_attempts = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)]
    )
    lockout_duration = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text='Account lockout duration in minutes'
    )

    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    maintenance_notifications = models.BooleanField(default=True)
    security_notifications = models.BooleanField(default=True)

    # Integration Settings
    google_api_key = models.CharField(max_length=255, blank=True)
    enable_google_login = models.BooleanField(default=False)
    enable_microsoft_login = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f"System Settings (Last updated: {self.updated_at})"

    @classmethod
    def get_settings(cls):
        """Get or create system settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
