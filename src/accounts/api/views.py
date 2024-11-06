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

from django.http import JsonResponse
import requests
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from accounts.models import User
from accounts.utils import get_management_token, requires_scope
from core.exceptions import GenericErrorException
from core.pagination import TablePagination
from core.permissions import AdminAccessPermission
from .serializers import ListUserSerializer, UserSerializer


class CurrentUserView(ListAPIView):
    serializer_class = ListUserSerializer
    print("CurrentUserView: Fetching current user data.", self.get_serializer(request.user, many=False))
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        print("CurrentUserView: Fetching current user data.")
        serializer = self.get_serializer(request.user, many=False)
        print("CurrentUserView: User data retrieved:", serializer.data)
        return Response(serializer.data)


class UserApiView(ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    action_serializer_class = UserSerializer
    pagination_class = TablePagination
    permission_classes = (IsAuthenticated, AdminAccessPermission)

    def post(self, request, *args, **kwargs):
        print("UserApiView: Creating new user.")
        serializer = self.action_serializer_class(data=request.data)
        print("UserApiView: Incoming request data:", request.data)

        serializer.is_valid(raise_exception=True)
        created_user = serializer.save()
        print("UserApiView: User created:", created_user)

        try:
            auth0_user = self.auth0_register(serializer)
            created_user.username = auth0_user['user_id'].replace('|', '.')
            created_user.save()
            print("UserApiView: Auth0 user registered:", auth0_user)
        except GenericErrorException as e:
            print("UserApiView: Error during user registration:", str(e))
            created_user.delete()
            raise e

        headers = self.get_success_headers(serializer.data)
        print("UserApiView: User created successfully, responding with data.")
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def auth0_register(self, serializer):
        print("UserApiView: Registering user with Auth0.")
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

        url = "https://dev-mgw72jpas4obd84e.us.auth0.com/api/v2/users"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_management_token()}"
        }

        print("UserApiView: Sending request to Auth0:", auth0_body)
        response = requests.post(url, json=auth0_body, headers=headers)

        if response.status_code not in [200, 201]:
            print("UserApiView: Auth0 registration failed with status:", response.status_code)
            raise GenericErrorException(response.json())

        print("UserApiView: Auth0 registration successful:", response.json())
        return response.json()

    def update(self, request, *args, **kwargs):
        print("UserApiView: Updating user.")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.action_serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        print("UserApiView: User updated successfully:", serializer.data)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def public(request):
    print("public: Accessing public endpoint route.")
    return JsonResponse({'message': 'Hello from a public endpoint! You don\'t need to be authenticated to see this.'})


@api_view(['GET'])
@permission_classes([AllowAny])
def private(request):
    print("private: Accessing private endpoint.")
    return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated to see this.'})


@api_view(['GET'])
@requires_scope('admin')
def private_scoped(request):
    print("private_scoped: Accessing scoped private endpoint.")
    return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this.'})
