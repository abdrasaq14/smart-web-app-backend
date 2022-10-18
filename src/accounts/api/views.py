from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from .serializers import UserSerializer


class CurrentUserView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user
