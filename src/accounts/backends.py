from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class RemoteUserBackend(ModelBackend):
    """
    This backend is to be used in conjunction with the ``RemoteUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.
    """

    def authenticate(self, request, remote_user):
        """"""
        if not remote_user:
            return

        user = None

        try:
            user = UserModel.objects.get(username=remote_user)
        except UserModel.DoesNotExist:
            pass

        return user if self.user_can_authenticate(user) else None


class BypassAuthBackend(ModelBackend):
    """Bypass auth"""

    def authenticate(self, request, remote_user):
        """"""
        return UserModel.objects.all().first()
