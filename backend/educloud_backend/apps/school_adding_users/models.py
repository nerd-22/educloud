from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from apps.schools.models import School
import binascii
import os

class SchoolUser(AbstractUser):
    ROLE_CHOICES = [
        ('REGISTRAR', 'Registrar'),
        ('FINANCIAL', 'Financial Officer'),
        ('ACCOUNTANT', 'Accountant'),
        ('VICE_PRINCIPAL', 'Vice Principal'),
        ('PRINCIPAL', 'Principal'),
        ('TEACHER', 'Teacher'),
        ('PARENT', 'Parent'),
        ('SECURITY', 'Security'),
    ]
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_users')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='school_user_set',
        related_query_name='school_user'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='school_user_set',
        related_query_name='school_user'
    )

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # If this is a parent, can link to their children
    children = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='parents')

    class Meta:
        app_label = 'school_adding_users'
        verbose_name = 'School User'
        verbose_name_plural = 'School Users'
        unique_together = ('school', 'username')

    def __str__(self):
        return f"{self.full_name} - {self.get_role_display()} at {self.school.name}"

class SchoolUserToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(
        'SchoolUser',
        related_name='school_user_token',
        on_delete=models.CASCADE,
        verbose_name="School User"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        app_label = 'school_adding_users'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
