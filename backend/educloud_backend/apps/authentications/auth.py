from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class SuperAdminSessionAuthentication(authentication.SessionAuthentication):
    """
    Custom session authentication for super admins that doesn't interfere with school admin token auth
    """
    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in super admin
        user. Otherwise returns `None`.
        """
        user = getattr(request._request, 'user', None)

        if not user or not user.is_authenticated:
            return None

        # Only handle super admin authentication here
        if not hasattr(user, 'is_super_admin') or not user.is_super_admin:
            return None

        logger.debug(f"Super admin authenticated: {user.username}")
        return (user, None)
