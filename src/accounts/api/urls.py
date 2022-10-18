


from django.urls import path
from accounts.api.views import CurrentUserView, UserApiView

urlpatterns = [
    path("users/me", CurrentUserView.as_view(), name="users-me"),
    path("users", UserApiView.as_view(), name="users"),
]
