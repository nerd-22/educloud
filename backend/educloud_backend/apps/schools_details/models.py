from django.db import models
from apps.schools.models import School, SchoolAdmin

class PaymentSetup(models.Model):
    PAYMENT_METHODS = [
        ('MOMO', 'Mobile Money'),
        ('CARD', 'Card Payment'),
        ('CASH', 'Cash Payment'),
    ]

    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='payment_setup')
    enabled_methods = models.JSONField(default=list)  # List of enabled payment methods
    momo_provider = models.CharField(max_length=50, blank=True)
    momo_number = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FeeStructure(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_structures')
    name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='invoices')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PaymentAlert(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='payment_alerts')
    days_before = models.IntegerField(help_text='Days before due date to send alert')
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SchoolDocument(models.Model):
    DOCUMENT_TYPES = [
        ('POLICY', 'School Policy'),
        ('HANDBOOK', 'Student Handbook'),
        ('CURRICULUM', 'Curriculum Guide'),
        ('OTHER', 'Other'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='school_docs/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(SchoolAdmin, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Communication(models.Model):
    MESSAGE_TYPES = [
        ('INTERNAL', 'Internal Message'),
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('NOTICE', 'Admin Notice'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='communications')
    sender = models.ForeignKey(SchoolAdmin, on_delete=models.SET_NULL, null=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_to = models.JSONField(help_text='List of recipient IDs and types')
    sent_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.JSONField(default=dict)

class SchoolDetails(models.Model):
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='details')
    
    # Additional School Information
    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    core_values = models.JSONField(default=list)  # List of core values
    
    # Academic Information
    accreditation_info = models.TextField(blank=True)
    accreditation_status = models.CharField(max_length=50, blank=True)
    accreditation_date = models.DateField(null=True, blank=True)
    renewal_date = models.DateField(null=True, blank=True)
    
    # Infrastructure
    total_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in square meters
    built_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in square meters
    num_buildings = models.IntegerField(null=True, blank=True)
    num_classrooms = models.IntegerField(null=True, blank=True)
    num_labs = models.IntegerField(null=True, blank=True)
    num_libraries = models.IntegerField(null=True, blank=True)
    sports_facilities = models.JSONField(default=list)  # List of available sports facilities
    
    # Staff Information
    num_teaching_staff = models.IntegerField(null=True, blank=True)
    num_non_teaching_staff = models.IntegerField(null=True, blank=True)
    student_teacher_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Academic Programs
    programs_offered = models.JSONField(default=list)  # List of academic programs
    languages_taught = models.JSONField(default=list)  # List of languages taught
    extra_curricular = models.JSONField(default=list)  # List of extra-curricular activities
    
    # Transportation
    has_transportation = models.BooleanField(default=False)
    num_buses = models.IntegerField(null=True, blank=True)
    transport_routes = models.JSONField(default=list)  # List of transport routes
    
    # Medical Facilities
    has_medical_room = models.BooleanField(default=False)
    num_medical_staff = models.IntegerField(null=True, blank=True)
    medical_facilities = models.JSONField(default=list)  # List of available medical facilities
    
    # Additional Facilities
    canteen_capacity = models.IntegerField(null=True, blank=True)
    has_smart_classes = models.BooleanField(default=False)
    has_solar_power = models.BooleanField(default=False)
    has_generator = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.school.name} Details"
    
    class Meta:
        verbose_name = 'School Details'
        verbose_name_plural = 'School Details'