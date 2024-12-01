
# import jwt
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed

# class CustomJWTAuthentication(JWTAuthentication):
#     def authenticate(self, request):
#         auth = request.headers.get('Authorization')
#         if not auth:
#             raise AuthenticationFailed("Authorization header missing.")
        
#         print("Authorization Header:", auth)
        
#         token = auth.split(" ")[1]  # Extract the token part
#         print("Extracted Token:", token)
        
#         try:
#             # Attempt to authenticate the token
#             auth_result = super().authenticate(request)
#             if not auth_result:
#                 return None
            
#             validated_token = auth_result[0]
#             user_id = validated_token.get('sub')  # Extract 'sub'
            
#             if not user_id:
#                 raise AuthenticationFailed("Token is missing user ID (sub).")

#             print("USERID:", user_id)  # Log user ID for debugging
#             return auth_result
        
#         except Exception as e:
#             print(f"Error during token validation: {e}")
#             raise AuthenticationFailed(f"Invalid token: {e}")

import requests
from jose import jwt
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User
from django.conf import settings
import logging

# Logger for debugging
logger = logging.getLogger(__name__)

# Constants for Auth0 and API configuration
AUTH0_DOMAIN = getattr(settings, 'AUTH0_DOMAIN', 'dev-mgw72jpas4obd84e.us.auth0.com')
API_IDENTIFIER = getattr(settings, 'API_IDENTIFIER', 'https://api.demo.powersmarter.net/')
ALGORITHMS = getattr(settings, 'ALGORITHMS', ['RS256'])
print("DETAILS", API_IDENTIFIER)
class CustomJWTAuthentication(BaseAuthentication):
    
    @staticmethod
    def get_jwk():
        """Fetch and cache public keys from Auth0"""
        jwks = cache.get('auth0_jwks')
        if not jwks:
            url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
            response = requests.get(url)
            jwks = response.json()['keys']
            print("JWKS", jwks)
            cache.set('auth0_jwks', jwks, timeout=86400)  # Cache for 1 day
        return jwks

    @staticmethod
    def validate_jwt(token):
        """Validate JWT with Auth0 public keys"""
        try:
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}

            for key in CustomJWTAuthentication.get_jwk():
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e'],
                    }

            if rsa_key:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_IDENTIFIER,
                    issuer=f'https://{AUTH0_DOMAIN}/'
                )
                print("Paylload", payload)
                return payload

            raise Exception("Unable to find appropriate key.")
        except Exception as e:
            logger.error(f"JWT validation failed: {str(e)}")
            raise AuthenticationFailed(f"Token validation failed: {str(e)}")

    def authenticate(self, request):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return None  # Allow unauthenticated access

        parts = auth.split()
        print("parts", parts)
        if len(parts) != 2:
            raise AuthenticationFailed('Authorization header must be in the form "Bearer <token>"')

        token = parts[1]
        payload = self.validate_jwt(token)
        print("authenticatevalidagte", payload)
        try:
            print("userObject", payload['sub'])
            user = User.objects.get(username=payload['sub'])
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found for the provided token.')

        return (user, token)
