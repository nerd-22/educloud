from django.contrib.auth.models import User
from django.core.validators import URLValidator
from rest_framework import serializers
from django.utils.dateparse import parse_date
from .models import School, SchoolAdmin
import re
import json

class SchoolAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolAdmin
        fields = ['id', 'full_name', 'email', 'phone_number', 'role', 'username']
        read_only_fields = ['id']

class SchoolSerializer(serializers.ModelSerializer):
    administrators = SchoolAdminSerializer(many=True, read_only=True)
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = '__all__'
        read_only_fields = ['id', 'school_code', 'login_url', 'created_at', 'updated_at', 'logo_url']
    
    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

class SchoolCreateSerializer(serializers.ModelSerializer):
    admin_full_name = serializers.CharField(write_only=True)
    admin_email = serializers.EmailField(write_only=True)
    admin_phone = serializers.CharField(write_only=True)
    admin_role = serializers.CharField(write_only=True, required=False, default='School Admin')
    academic_levels = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=True
    )
    school_year_start = serializers.DateField()
    school_year_end = serializers.DateField()

    class Meta:
        model = School
        fields = '__all__'
        read_only_fields = ['id', 'school_code', 'login_url', 'created_at', 'updated_at']

    def validate(self, data):
        if data['school_year_end'] <= data['school_year_start']:
            raise serializers.ValidationError({
                'school_year_end': 'School year end date must be after start date'
            })
        return data

    def validate_year_established(self, value):
        current_year = 2025  # You might want to import datetime to get current year
        if value < 1800 or value > current_year:
            raise serializers.ValidationError(f"Year established must be between 1800 and {current_year}")
        return value

    def validate_phone_number(self, value):
        # Basic phone number validation - adjust regex as needed
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value

    def validate_admin_phone(self, value):
        # Validate admin phone number
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Invalid administrator phone number format")
        return value

    def validate_website(self, value):
        if value:
            try:
                URLValidator()(value)
            except:
                raise serializers.ValidationError("Invalid website URL")
        return value

    def create(self, validated_data):
        # Extract admin data
        admin_data = {
            'full_name': validated_data.pop('admin_full_name'),
            'email': validated_data.pop('admin_email'),
            'phone_number': validated_data.pop('admin_phone'),
            'role': validated_data.pop('admin_role', 'School Admin')
        }

        # First create the school
        school = School.objects.create(**validated_data)
        
        # Generate a random password
        from django.contrib.auth.hashers import make_password
        from django.utils.crypto import get_random_string
        from django.core.mail import send_mail
        from django.conf import settings
        
        password = get_random_string(12)  # Generate a 12-character random password
        username = admin_data['email'].split('@')[0]
        
        # Create the admin user and school admin
        admin = SchoolAdmin.objects.create(
            school=school,
            username=username,
            email=admin_data['email'],
            full_name=admin_data['full_name'],
            phone_number=admin_data['phone_number'],
            role=admin_data['role'],
            is_school_admin=True
        )
        admin.set_password(password)
        admin.save()

        # Send credentials via email
        try:
            send_mail(
                subject='Welcome to EduCloud - Your School Administrator Account',
                message=f"""
Dear {admin_data['full_name']},

Your school administrator account has been created for {school.name}.

Login Details:
- School Code: {school.school_code}
- Username: {username}
- Password: {password}

Login URL: {school.login_url}

Please change your password after your first login.

Best regards,
EduCloud Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_data['email']],
                fail_silently=False
            )
        except Exception as e:
            # Log the error but don't prevent school creation
            self._errors['email_warning'] = f"School created but failed to send admin credentials: {str(e)}"

        return school
