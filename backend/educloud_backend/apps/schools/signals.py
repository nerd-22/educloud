from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import School, SchoolAdmin

# Email sending is now handled in SchoolCreateSerializer
@receiver(post_save, sender=SchoolAdmin)
def setup_school_admin(sender, instance, created, **kwargs):
    """
    Signal handler to perform any necessary setup for newly created school admins.
    Email sending is handled in the SchoolCreateSerializer.
    """
    if created and instance.is_school_admin:
        # Additional setup can be added here if needed
        pass
