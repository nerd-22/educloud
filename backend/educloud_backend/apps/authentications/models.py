from django.db import models
from django.contrib.auth.models import AbstractUser

class SuperAdmin(AbstractUser):
    email = models.EmailField(unique=True)
    is_super_admin = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='super_admin_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='super_admin_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Super Admin'
        verbose_name_plural = 'Super Admins'
        app_label = 'authentications'

    def __str__(self):
        return self.email
