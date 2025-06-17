from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import SchoolAdmin, SchoolAdminToken
import logging

logger = logging.getLogger(__name__)

class SchoolAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
            
        try:
            # Try to fetch the user by username or email
            user = SchoolAdmin.objects.get(
                Q(username=username) | Q(email=username)
            )
            
            logger.debug(f"Found school admin for authentication: {user}")
            
            if user.check_password(password):
                logger.debug("School admin password check successful")
                return user
            
            logger.debug("School admin password check failed")
            return None
            
        except SchoolAdmin.DoesNotExist:
            logger.debug(f"No SchoolAdmin found for username/email: {username}")
            return None

    def get_user(self, user_id):
        try:
            return SchoolAdmin.objects.get(pk=user_id)
        except SchoolAdmin.DoesNotExist:
            return None

class SchoolAdminTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the Authorization header
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        logger.debug(f"Received Authorization header: {auth}")
        
        if not auth:
            logger.debug("No Authorization header found")
            return None
            
        auth_parts = auth.split()
        if not auth_parts or auth_parts[0].lower() != 'token':
            logger.debug(f"Invalid token type: {auth_parts[0] if auth_parts else 'none'}")
            return None
            
        if len(auth_parts) != 2:
            logger.debug(f"Invalid token format - expected 2 parts, got {len(auth_parts)}")
            return None
        
        token = auth_parts[1]
        logger.debug(f"Processing token: {token[:10]}...")
        
        # Extract school code from URL path
        path_parts = request.path.split('/')
        if 'schools' in path_parts:
            try:
                school_code_index = path_parts.index('schools') + 1
                # Skip authentication for admin routes
                if len(path_parts) > school_code_index and path_parts[school_code_index] == 'admins':
                    logger.debug("Admin route detected, skipping school code validation")
                    requested_school_code = None
                else:
                    requested_school_code = path_parts[school_code_index]
                    logger.debug(f"Requested school code from URL: {requested_school_code}")
            except (IndexError, ValueError):
                requested_school_code = None
                logger.debug("No school code found in URL")
        else:
            requested_school_code = None
            logger.debug("Not a school-specific route")
            
        try:
            token_obj = SchoolAdminToken.objects.select_related('user', 'user__school').get(key=token)
            if not token_obj.user.is_active:
                logger.debug("User is not active")
                return None
                
            # Only verify school matches for school-specific endpoints
            if requested_school_code and token_obj.user.school.school_code != requested_school_code:
                logger.debug(f"Token school ({token_obj.user.school.school_code}) doesn't match requested school ({requested_school_code})")
                return None
                
            logger.debug(f"Successfully authenticated user for school: {token_obj.user.school.school_code}")
            return (token_obj.user, token_obj)
        except SchoolAdminToken.DoesNotExist:
            logger.debug("Token not found in database")
            return None
