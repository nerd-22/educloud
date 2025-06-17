from rest_framework import serializers
from .models import (
    PaymentSetup, FeeStructure, Invoice, PaymentAlert,
    SchoolDocument, Communication, SchoolDetails
)
from apps.schools.serializers import SchoolAdminSerializer, SchoolSerializer

class PaymentSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSetup
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class InvoiceSerializer(serializers.ModelSerializer):
    fee_structure_details = FeeStructureSerializer(source='fee_structure', read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'invoice_number']

    def create(self, validated_data):
        # Generate unique invoice number
        import uuid
        validated_data['invoice_number'] = f"INV-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)

class PaymentAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAlert
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class SchoolDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_details = SchoolAdminSerializer(source='uploaded_by', read_only=True)

    class Meta:
        model = SchoolDocument
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'uploaded_by_details']

class CommunicationSerializer(serializers.ModelSerializer):
    sender_details = SchoolAdminSerializer(source='sender', read_only=True)

    class Meta:
        model = Communication
        fields = '__all__'
        read_only_fields = ['sent_at', 'sender_details']

    def validate_sent_to(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("sent_to must be a list of recipient details")
        for recipient in value:
            if not isinstance(recipient, dict) or 'id' not in recipient or 'type' not in recipient:
                raise serializers.ValidationError("Each recipient must have 'id' and 'type' fields")
        return value

class SchoolDetailsSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)

    class Meta:
        model = SchoolDetails
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_student_teacher_ratio(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("Student-teacher ratio must be a positive number")
        return value
    
    def validate_core_values(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Core values must be a list")
        return value
    
    def validate_sports_facilities(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Sports facilities must be a list")
        return value
    
    def validate_programs_offered(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Programs offered must be a list")
        return value
    
    def validate_languages_taught(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Languages taught must be a list")
        return value
    
    def validate_transport_routes(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Transport routes must be a list")
        return value
    
    def validate_medical_facilities(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Medical facilities must be a list")
        return value