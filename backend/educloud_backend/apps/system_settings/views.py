from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SystemSettings
from .serializers import SystemSettingsSerializer
from apps.authentications.models import SuperAdmin


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def system_settings(request):
    """
    GET: Retrieve system settings
    PUT: Update system settings
    """
    # Check if user is a super admin
    if not isinstance(request.user, SuperAdmin):
        return Response(
            {'error': 'Only super admins can access system settings'},
            status=status.HTTP_403_FORBIDDEN
        )

    settings = SystemSettings.get_settings()

    if request.method == 'GET':
        serializer = SystemSettingsSerializer(settings)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SystemSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.
