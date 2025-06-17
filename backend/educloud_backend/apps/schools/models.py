from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import URLValidator
from django.utils.crypto import get_random_string
import uuid
import binascii
import os

def school_logo_path(instance, filename):
    # Generate a unique filename for each school's logo
    ext = filename.split('.')[-1]
    return f'school_logos/{instance.school_code}/{uuid.uuid4()}.{ext}'

class School(models.Model):
    SCHOOL_TYPES = [
        ('PRIMARY', 'Primary School'),
        ('SECONDARY', 'Secondary School'),
        ('HIGH_SCHOOL', 'High School'),
        ('COLLEGE', 'College'),
    ]
    
    OWNERSHIP_TYPES = [
        ('PRIVATE', 'Private'),
        ('PUBLIC', 'Public'),
        ('MISSION', 'Mission'),
    ]

    TERM_STRUCTURES = [
        ('2_TERMS', '2 Terms'),
        ('3_TERMS', '3 Terms'),
        ('SEMESTER', 'Semester'),
    ]

    # Basic Information
    name = models.CharField(max_length=255)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPES)
    school_code = models.CharField(max_length=50, unique=True, blank=True)
    registration_number = models.CharField(max_length=100, unique=True)
    motto = models.CharField(max_length=255, blank=True)
    year_established = models.IntegerField()
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_TYPES)

    # Contact & Address
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_address = models.TextField()
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True, validators=[URLValidator()])
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    # Academic Details
    num_campuses = models.IntegerField(default=1)
    academic_levels = models.JSONField()
    num_students = models.IntegerField()
    num_teachers = models.IntegerField()
    grading_system = models.CharField(max_length=50)
    curriculum_type = models.CharField(max_length=100)

    # Facilities
    has_boarding = models.BooleanField(default=False)
    has_online_classes = models.BooleanField(default=False)
    has_library = models.BooleanField(default=False)
    has_laboratories = models.BooleanField(default=False)
    has_computer_lab = models.BooleanField(default=False)
    has_sports_complex = models.BooleanField(default=False)
    has_cafeteria = models.BooleanField(default=False)

    # Documents
    logo = models.ImageField(upload_to=school_logo_path, null=True, blank=True)
    accreditation_cert = models.FileField(upload_to='school_docs/', null=True, blank=True)
    registration_docs = models.FileField(upload_to='school_docs/', null=True, blank=True)

    # System Settings
    default_language = models.CharField(max_length=50, default='English')
    currency = models.CharField(max_length=10)
    timezone = models.CharField(max_length=50)
    school_year_start = models.DateField()
    school_year_end = models.DateField()
    term_structure = models.CharField(max_length=20, choices=TERM_STRUCTURES)

    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    login_url = models.URLField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def generate_school_code(self):
        if not self.school_code:
            self.school_code = f"SCH-{uuid.uuid4().hex[:8].upper()}"

    def save(self, *args, **kwargs):
        self.generate_school_code()
        if not self.login_url:
            # For development, using localhost. In production, use actual domain
            self.login_url = f"http://localhost:3000/school/{self.school_code}/login"
        super().save(*args, **kwargs)

class SchoolAdminToken(models.Model):
    """
    Custom token model for SchoolAdmin authentication
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(
        'SchoolAdmin',
        related_name='auth_token',
        on_delete=models.CASCADE,
        verbose_name="School Admin"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "School Admin Token"
        verbose_name_plural = "School Admin Tokens"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

class SchoolAdmin(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('REGISTRAR', 'Registrar'),
        ('FINANCIAL', 'Financial Officer'),
        ('ACCOUNTANT', 'Accountant'),
        ('VICE_PRINCIPAL', 'Vice Principal'),
        ('PRINCIPAL', 'Principal'),
        ('TEACHER', 'Teacher'),
        ('PARENT', 'Parent'),
        ('SECURITY', 'Security'),
    ]

    school = models.ForeignKey(School, related_name='administrators', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ADMIN')
    is_school_admin = models.BooleanField(default=True)
    
    # Use email as username field
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name', 'phone_number']
    
    def generate_auth_token(self):
        """Generate or get authentication token for the admin"""
        token, created = SchoolAdminToken.objects.get_or_create(user=self)
        return token.key

    def __str__(self):
        return self.full_name
