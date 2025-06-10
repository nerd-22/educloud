from rest_framework import serializers
from .models import SuperAdmin

class SuperAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = ['id', 'email', 'username', 'is_super_admin', 'is_staff']
        read_only_fields = ['is_super_admin', 'is_staff']
