from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from .serializers import SuperAdminSerializer
from .models import SuperAdmin
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes([AllowAny])
def get_csrf_token(request):
    logger.debug("CSRF token requested")
    return Response({'detail': 'CSRF cookie set'})

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    logger.debug(f"Super admin login attempt for email: {email}")
    
    try:
        user = SuperAdmin.objects.get(email=email)
        auth_user = authenticate(request, username=user.username, password=password)
        
        if auth_user is not None and auth_user.is_super_admin:
            login(request, auth_user)
            serializer = SuperAdminSerializer(auth_user)
            logger.debug(f"Super admin login successful: {auth_user.username}")
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'user': serializer.data
            })
        else:
            logger.warning(f"Invalid credentials for email: {email}")
            return Response({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    except SuperAdmin.DoesNotExist:
        logger.warning(f"No super admin found for email: {email}")
        return Response({
            'status': 'error',
            'message': 'User not found'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return Response({
        'status': 'success',
        'message': 'Logout successful'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    if not hasattr(request.user, 'is_super_admin') or not request.user.is_super_admin:
        return Response({
            'status': 'error',
            'message': 'Not authorized'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = SuperAdminSerializer(request.user)
    return Response({
        'status': 'success',
        'user': serializer.data
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def create_default_admin(request):
    # Check if default admin exists
    if not SuperAdmin.objects.filter(email='admin@educloud.com').exists():
        admin = SuperAdmin.objects.create(
            username='admin',
            email='admin@educloud.com',
            is_super_admin=True,
            is_staff=True,
            is_superuser=True
        )
        admin.set_password('admin123')
        admin.save()
        return Response({
            'status': 'success',
            'message': 'Default admin created successfully'
        })
    return Response({
        'status': 'error',
        'message': 'Default admin already exists'
    })
