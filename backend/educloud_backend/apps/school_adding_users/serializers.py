from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import SchoolUser

class SchoolUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = SchoolUser
        fields = [
            'id', 'username', 'password', 'confirm_password', 'email', 'full_name', 
            'phone_number', 'role', 'role_display', 'is_active', 'school', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'full_name': {'required': True},
            'role': {'required': True},
        }
        
    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({
                "password": "Passwords do not match"
            })
        return data

    def create(self, validated_data):
        # Remove confirm_password as it's not needed in the model
        validated_data.pop('confirm_password', None)
        
        # Hash the password
        validated_data['password'] = make_password(validated_data.get('password'))
        
        # Set is_active to True by default
        validated_data['is_active'] = True
        
        return super().create(validated_data)

class SchoolUserListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = SchoolUser
        fields = ['id', 'username', 'email', 'full_name', 'phone_number', 'role', 'role_display', 'is_active']
