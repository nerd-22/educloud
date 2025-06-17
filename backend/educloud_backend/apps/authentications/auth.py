from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from apps.school_adding_users.models import SchoolUserToken, SchoolUser
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class CustomModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            # Try to fetch the user by username or email
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
            
            if user.check_password(password):
                return user
                
            return None
            
        except User.DoesNotExist:
            return None

class CustomTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom token based authentication that works with our SchoolUserToken model
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
        if not auth_header or auth_header[0].lower() != 'token':
            return None

        if len(auth_header) != 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = SchoolUserToken.objects.select_related('user').get(key=auth_header[1])
        except SchoolUserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        # Add the token to the request so we can access it in the views
        request.auth_token = token

        return (token.user, token)
