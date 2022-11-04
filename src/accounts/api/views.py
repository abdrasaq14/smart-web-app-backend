from django.http import JsonResponse
import requests
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from accounts.models import User
from accounts.utils import get_token_auth_header, requires_scope
from core.exceptions import GenericErrorException
from core.pagination import TablePagination
from core.permissions import AdminAccessPermission
from .serializers import ListUserSerializer, UserSerializer


class CurrentUserView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return [self.request.user]


class UserApiView(ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    action_serializer_class = UserSerializer
    pagination_class = TablePagination
    permission_classes = (IsAuthenticated, AdminAccessPermission)

    def post(self, request, *args, **kwargs):
        serializer = self.action_serializer_class(data=request.data)

        auth0_user = self.auth0_register(serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save(username=auth0_user['user_id'])

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

        url = "https://dev-u0pz-ez1.eu.auth0.com/api/v2/users"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_token_auth_header(self.request)}"
        }

        response = requests.request("POST", url, json=auth0_body, headers=headers)

        if response.status_code not in [200, 201]:
            # import ipdb ; ipdb.set_trace()
            raise GenericErrorException(f"Cannot register user: {response.text}")

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
