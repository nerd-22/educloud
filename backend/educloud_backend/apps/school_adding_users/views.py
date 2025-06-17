from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from .models import SchoolUser, SchoolUserToken
from .serializers import SchoolUserSerializer, SchoolUserListSerializer
import logging

logger = logging.getLogger(__name__)

class SchoolUserViewSet(viewsets.ModelViewSet):
    queryset = SchoolUser.objects.all()
    serializer_class = SchoolUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return SchoolUser.objects.none()
            
        # If user is a SchoolAdmin, return users from their school
        if hasattr(user, 'school') and user.school:
            return SchoolUser.objects.filter(school=user.school)
            
        # For superusers, return all users
        if user.is_superuser:
            return SchoolUser.objects.all()
            
        return SchoolUser.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return SchoolUserListSerializer
        return SchoolUserSerializer
    
    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'school'):
            return Response(
                {'error': 'Only school administrators can create users'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            with transaction.atomic():
                # Add the school to the data
                data = request.data.copy()
                data['school'] = request.user.school.id
                
                # Create and validate the user
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()

                # Create token for the new user
                token = SchoolUserToken.objects.create(user=user)

                try:
                    # Send welcome email
                    send_mail(
                        subject='Welcome to EduCloud - Your School Account',
                        message=f"""
Dear {user.full_name},

Your account has been created for {user.school.name}.

Login Details:
- School Code: {user.school.school_code}
- Username: {user.username}
- Password: {data.get('password')}
- Role: {user.get_role_display()}

Please change your password after your first login.

Best regards,
EduCloud Team
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True
                    )
                except Exception as e:
                    logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")

                return Response({
                    'message': 'User created successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'role': user.role,
                        'role_display': user.get_role_display(),
                        'school_code': user.school.school_code,
                        'token': token.key,
                    }
                }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({
                'error': 'Validation error',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return Response({
                'error': 'Failed to create user',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        school_code = request.data.get('school_code')

        if not all([username, password, school_code]):
            return Response(
                {'error': 'Please provide username, password and school code'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = SchoolUser.objects.get(
                username=username, 
                school__school_code=school_code
            )

            if not user.check_password(password):
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not user.is_active:
                return Response(
                    {'error': 'This account is inactive'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            token = SchoolUserToken.objects.create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'role_display': user.get_role_display(),
                    'school_code': school_code,
                }
            })

        except SchoolUser.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': 'Login failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
        def create(self, request, *args, **kwargs):
            if not hasattr(request.user, 'school'):
                return Response(
                    {'error': 'Only school administrators can create school users'},
                    status=status.HTTP_403_FORBIDDEN
                )

        try:
            with transaction.atomic():
                # Create the user with the school admin's school
                data = request.data.copy()
                data['school'] = request.user.school.id

                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                
                # Save the user
                user = serializer.save()
                
                # Create token for the new user
                token = SchoolUserToken.objects.create(user=user)

                # Send welcome email
                try:
                    send_mail(
                        subject='Welcome to EduCloud - Your School Account',
                        message=f"""
Dear {user.full_name},

Your account has been created for {user.school.name}.

Login Details:
- School Code: {user.school.school_code}
- Username: {user.username}
- Password: {data.get('password')}
- Role: {user.get_role_display()}

Please change your password after your first login.

Best regards,
EduCloud Team
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True
                    )
                except Exception as e:
                    logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")

                return Response({
                    'message': 'User created successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'role': user.role,
                        'role_display': user.get_role_display(),
                        'school_code': user.school.school_code,
                    }
                }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response(
                {'error': 'Validation error', 'details': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating school user: {str(e)}")
            return Response(
                {'error': 'Failed to create user. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        new_password = SchoolUser.objects.make_random_password()
        user.set_password(new_password)
        user.save()

        try:
            send_mail(
                subject='EduCloud - Password Reset',
                message=f"""
Dear {user.full_name},

Your password has been reset.

New Password: {new_password}

Please change your password after login.

Best regards,
EduCloud Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            return Response({'status': 'password reset successful'})
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        school_code = request.data.get('school_code')

        if not all([username, password, school_code]):
            return Response(
                {'error': 'Please provide username, password and school code'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = SchoolUser.objects.get(username=username, school__school_code=school_code)
            if not user.check_password(password):
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not user.is_active:
                return Response(
                    {'error': 'This account is inactive'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            token, _ = SchoolUserToken.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'school_code': school_code,
                }
            })
        except SchoolUser.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED            )
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': 'Login failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
