import base64
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from munch.models import Server

class ServerBasicAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
        # check if not basic auth
        if not auth_header.startswith('Basic '):
            return None 
        
        # decode username and password from auth header
        try:
            decoded_login = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = decoded_login.split(':', 1)
        except Exception:
            raise AuthenticationFailed('Invalid Basic Auth header')
        
        # check db if server connection exists
        # storing passwords as plaintext for now
        try:
            origin = request.META.get('HTTP_ORIGIN', '')
            server = Server.objects.get(url=origin, username=username, password=password, is_approved=True)
        except Server.DoesNotExist:
            raise AuthenticationFailed('Invalid credentials')
        
        return (server, 'basic')