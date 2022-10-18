


from django.urls import path
from accounts.api.views import CurrentUserView

urlpatterns = [
    path("users/me", CurrentUserView.as_view(), name="users-me"),
]
