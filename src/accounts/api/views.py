from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User
from core.pagination import TablePagination
from .serializers import ListUserSerializer, UserSerializer


class CurrentUserView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user


class UserApiView(ListAPIView, CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    action_serializer_class = UserSerializer
    pagination_class = TablePagination

    def post(self, request, *args, **kwargs):
        serializer = self.action_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
