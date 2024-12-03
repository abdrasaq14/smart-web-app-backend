# from django.http import JsonResponse
# import requests
# from functools import wraps
# from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework import status
# from accounts.models import User
# from accounts.utils import get_management_token, get_token_auth_header
# from core.exceptions import GenericErrorException
# from core.pagination import TablePagination
# from core.permissions import AdminAccessPermission              
# from .serializers import ListUserSerializer, UserSerializer     
# import jwt

# def requires_permission(required_permission):
#     """Decorator to check if a specific permission is present in the user's JWT token."""
#     def require_permission(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             token = get_token_auth_header(args[0])
#             decoded = jwt.decode(token, options={"verify_signature": False})
#             if decoded.get("permissions"):
#                 token_permissions = decoded["permissions"]
#                 if required_permission in token_permissions:
#                     return f(*args, **kwargs)
#             response = JsonResponse({'message': 'You don\'t have the required permission'})
#             response.status_code = 403
#             return response
#         return decorated
#     return require_permission

# class CurrentUserView(ListAPIView):
#     serializer_class = ListUserSerializer
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, *args, **kwargs):
#         serializer = self.get_serializer(request.user, many=False)
#         return Response(serializer.data)

# class UserApiView(ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = ListUserSerializer
#     action_serializer_class = UserSerializer
#     pagination_class = TablePagination
#     permission_classes = (IsAuthenticated, AdminAccessPermission)

#     def post(self, request, *args, **kwargs):
#         serializer = self.action_serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         created_user = serializer.save()

#         try:
#             auth0_user = self.auth0_register(serializer)
#             created_user.username = auth0_user['user_id'].replace('|', '.')
#             created_user.save()
#         except GenericErrorException as e:
#             created_user.delete()
#             raise e

#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#     def auth0_register(self, serializer):
#         data = self.request.data
#         auth0_body = {
#             "email": data['email'],
#             "blocked": False,
#             "email_verified": False,
#             "given_name": data['first_name'],
#             "family_name": data['last_name'],
#             "name": f"{data['first_name']} {data['last_name']}",
#             "connection": "Username-Password-Authentication",
#             "verify_email": True,
#             "password": "Sm@rterise123"
#         }

#         url = "https://dev-mgw72jpas4obd84e.us.auth0.com/api/v2/users"
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {get_management_token()}" 
#         }

#         response = requests.post(url, json=auth0_body, headers=headers)

#         if response.status_code not in [200, 201]:
#             raise GenericErrorException(response.json())

#         return response.json()

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.action_serializer_class(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def public(request):
#     return JsonResponse({'message': 'Hello from a public endpoint! You don\'t need to be authenticated to see this.'})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def private(request):
#     return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated to see this.'})

# @api_view(['GET'])
# @requires_permission('admin:access')
# def private_scoped(request):
#     return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated and have the admin:access permission to see this.'})

import os
from django.http import JsonResponse
import jwt
import requests
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from accounts.models import User
from accounts.utils import get_management_token, requires_scope
from authentication.custom_authentication import CustomJWTAuthentication
from core.exceptions import GenericErrorException
from core.pagination import TablePagination
from core.permissions import AdminAccessPermission
from .serializers import ListUserSerializer, UserSerializer


from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

auth0_domain = os.environ.get('AUTH0_DOMAIN')
class CurrentUserView(ListAPIView):
    serializer_class = ListUserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        
        try:
            # Extract the token from the Authorization header
            auth_header = request.headers.get('Authorization', None)
            if not auth_header:
                raise AuthenticationFailed("Authorization header is missing.")

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise AuthenticationFailed('Authorization header must be in the form "Bearer <token>".')

            auth_token = parts[1]

            # Validate and decode the token using the custom authentication method
            decoded_token = CustomJWTAuthentication.validate_jwt(auth_token)
           
        except Exception as e:
            raise AuthenticationFailed(f"Token is invalid: {e}")

        # Fetch and serialize the current user
        serializer = self.get_serializer(request.user, many=False)
        return Response(serializer.data)



class UserApiView(ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    action_serializer_class = UserSerializer
    pagination_class = TablePagination
    permission_classes = (IsAuthenticated, AdminAccessPermission)

    def post(self, request, *args, **kwargs):
        serializer = self.action_serializer_class(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        created_user = serializer.save()
        
        try:
            auth0_user = self.auth0_register(serializer)
            # This is field is currently not validated to be a compulsory field as users are creatad without this
            # created_user.username = auth0_user['user_id'].replace('|', '.') #this is comflicting with auth0 as autho user_id is stored as auth0|67555
            created_user.username = auth0_user['user_id'] #this is comflicting with auth0 as autho user_id is stored as auth0|67555
            created_user.save()
           
        except GenericErrorException as e:
            created_user.delete()
            raise e

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def auth0_register(self, serializer):
        data = self.request.data
        auth0_body = {
            "email": data['email'],
            "blocked": False,
            "email_verified": False,
            "given_name": data['first_name'],
            "family_name": data['last_name'],
            "name": f"{data['first_name']} {data['last_name']}",
            "connection": "Username-Password-Authentication",
            "verify_email": True,
            "password": "Sm@rterise123"
        }

        # url = "https://dev-mgw72jpas4obd84e.us.auth0.com/api/v2/users"
        url =  'https://{}/api/v2/users'.format(auth0_domain)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_management_token()}"
        }

        response = requests.post(url, json=auth0_body, headers=headers)

        if response.status_code not in [200, 201]:
            raise GenericErrorException(response.json())

        return response.json()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.action_serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def public(request):
    return JsonResponse({'message': 'Hello from a public endpoint! You don\'t need to be authenticated to see this.'})


@api_view(['GET'])
def private(request):
    return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated to see this.'})


@api_view(['GET'])
@requires_scope('admin')
def private_scoped(request):
    return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this.'})
