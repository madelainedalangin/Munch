from rest_framework.permissions import BasePermission
from munch.models import Server

class IsAuthorizedServer(BasePermission):
    message = 'Access restricted to authorized remote nodes'

    def has_permission(self, request, view):
        return ( 
            request.auth == 'basic'
            and isinstance(request.user, Server)
            and request.user.is_approved
        )
    