from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import Http404
from django.utils import timezone
import logging
from .models import School, SchoolAdmin, SchoolAdminToken
from .serializers import SchoolSerializer, SchoolCreateSerializer, SchoolAdminSerializer
from .auth import SchoolAdminTokenAuthentication

logger = logging.getLogger(__name__)

class SchoolPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow any access for login and public info
        if view.action in ['school_login', 'public_info']:
            return True
            
        # For other actions, require authentication
        if not request.user or not request.user.is_authenticated:
            logger.debug(f"User not authenticated for action {view.action}")
            return False
            
        # Allow super admin access to everything
        if hasattr(request.user, 'is_super_admin') and request.user.is_super_admin:
            return True
            
        # For school admins
        if hasattr(request.user, 'is_school_admin') and request.user.is_school_admin:
            # Allow dashboard access for school admins
            if view.action in ['dashboard', 'retrieve']:
                return True
            if view.action == 'list':
                # School admins can only list their own school
                return True
            return True
            
        return False

    def has_object_permission(self, request, view, obj):
        # Allow public access for public info
        if view.action == 'public_info':
            return True

        # Allow super admin access to everything
        if hasattr(request.user, 'is_super_admin') and request.user.is_super_admin:
            return True
            
        # For school admins, only allow access to their own school
        if hasattr(request.user, 'is_school_admin') and request.user.is_school_admin:
            if view.action in ['dashboard', 'retrieve']:
                # For dashboard and retrieve, check if the school matches
                return request.user.school == obj
            return request.user.school == obj
            
        return False

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    permission_classes = [SchoolPermission]
    lookup_field = 'school_code'
    lookup_url_kwarg = 'school_code'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_object(self):
        """
        Retrieve a School instance by school_code
        """
        try:
            obj = School.objects.get(school_code=self.kwargs[self.lookup_url_kwarg])
            self.check_object_permissions(self.request, obj)
            return obj
        except School.DoesNotExist:
            raise Http404
            
    def get_queryset(self):
        logger.debug(f"User: {self.request.user}")
        logger.debug(f"Is authenticated: {self.request.user.is_authenticated}")
        logger.debug(f"Auth header: {self.request.headers.get('Authorization')}")
        logger.debug(f"Is super admin: {getattr(self.request.user, 'is_super_admin', False)}")
        logger.debug(f"Is school admin: {getattr(self.request.user, 'is_school_admin', False)}")
        
        if hasattr(self.request.user, 'is_super_admin') and self.request.user.is_super_admin:
            return School.objects.all()
        elif hasattr(self.request.user, 'is_school_admin') and self.request.user.is_school_admin:
            return School.objects.filter(id=self.request.user.school.id)
        return School.objects.none()
        
    def get_serializer_class(self):
        if self.action == 'create':
            return SchoolCreateSerializer
        return SchoolSerializer

    @action(detail=True, methods=['post'], url_path='login', permission_classes=[permissions.AllowAny], lookup_field='school_code')
    def school_login(self, request, school_code=None):
        """
        Login endpoint for school administrators.
        """
        try:
            school = School.objects.get(school_code=school_code)
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found with the provided code'},
                status=status.HTTP_404_NOT_FOUND
            )

        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Please provide both username/email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try to authenticate with username/email
        user = authenticate(request, username=username, password=password)
        
        logger.debug(f"Login attempt for school {school_code}")
        logger.debug(f"User authenticated: {user}")

        if not user:
            return Response(
                {'error': 'Invalid credentials. Please try again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_school_admin:
            return Response(
                {'error': 'User is not a school administrator'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.school != school:
            return Response(
                {'error': 'User is not associated with this school'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update last login
        user.last_login = timezone.now()
        user.save()

        # Create or get the authentication token
        token, _ = SchoolAdminToken.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'school_code': school.school_code,
                'school_name': school.name
            }
        })

    @action(detail=True, methods=['get'], lookup_field='school_code', authentication_classes=[SchoolAdminTokenAuthentication])
    def dashboard(self, request, school_code=None):
        """
        Get school dashboard data for authenticated school admin
        """
        logger.debug(f"Dashboard request for school {school_code}")
        logger.debug(f"User: {request.user}")
        logger.debug(f"Is authenticated: {request.user.is_authenticated}")
        logger.debug(f"Is school admin: {getattr(request.user, 'is_school_admin', False)}")
        logger.debug(f"Auth header: {request.headers.get('Authorization')}")
        
        try:
            school = self.get_object()
        except Http404:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not request.user.is_authenticated:
            logger.error("User not authenticated")
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not hasattr(request.user, 'is_school_admin') or not request.user.is_school_admin:
            logger.error(f"User {request.user.username} is not a school admin")
            return Response(
                {'error': 'User is not a school administrator'},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user.school != school:
            logger.warning(f"User school: {request.user.school.school_code}, Requested school: {school.school_code}")
            return Response(
                {'error': 'User does not belong to this school'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get school dashboard data
        serializer = self.get_serializer(school)
        data = {
            'school': serializer.data,
            'stats': {
                'total_students': getattr(school, 'num_students', 0),
                'total_teachers': getattr(school, 'num_teachers', 0),
                'total_campuses': getattr(school, 'num_campuses', 0),
                'academic_levels': getattr(school, 'academic_levels', []),
            },
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'full_name': request.user.full_name,
                'phone_number': request.user.phone_number,                'role': request.user.role
            }
        }
        return Response(data)

    @action(detail=True, methods=['get'], url_path='public-info', permission_classes=[permissions.AllowAny], lookup_field='school_code')
    def public_info(self, request, school_code=None):
        """
        Public endpoint to get basic school info without authentication
        """
        try:
            school = School.objects.get(school_code=school_code)
            data = {
                'name': school.name,
                'school_code': school.school_code,
                'logo_url': request.build_absolute_uri(school.logo.url) if school.logo else None,
            }
            return Response(data)
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SchoolAdminViewSet(viewsets.ModelViewSet):
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'is_super_admin') and self.request.user.is_super_admin:
            return SchoolAdmin.objects.all()
        elif hasattr(self.request.user, 'is_school_admin') and self.request.user.is_school_admin:
            return SchoolAdmin.objects.filter(school=self.request.user.school)
        return SchoolAdmin.objects.none()

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        admin = self.get_object()
        password = SchoolAdmin.objects.make_random_password()
        admin.set_password(password)
        admin.save()

        try:
            send_mail(
                subject='EduCloud - Password Reset',
                message=f"""
                Your password has been reset.
                
                New Password: {password}
                
                Please change your password after login.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                fail_silently=False
            )
            return Response({'status': 'password reset successful'})
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def update_password(self, request):
        """
        Update the password for the logged-in school admin.
        Requires current password and new password.
        """
        if not request.user.is_school_admin:
            return Response(
                {'error': 'Only school administrators can update their passwords'},
                status=status.HTTP_403_FORBIDDEN
            )

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'error': 'Both current and new passwords are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify current password
        if not request.user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate new password
        if len(new_password) < 8:
            return Response(
                {'error': 'New password must be at least 8 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        request.user.set_password(new_password)
        request.user.save()

        try:
            # Send email notification
            send_mail(
                subject='EduCloud - Password Updated',
                message=f"""
Hi {request.user.full_name},

Your password has been successfully updated.

If you did not make this change, please contact support immediately.

Best regards,
EduCloud Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to send password update email: {str(e)}")

        return Response({'status': 'Password updated successfully'})
