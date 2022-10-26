from django.urls import path
from accounts.api import views

urlpatterns = [
    path("users/me", views.CurrentUserView.as_view(), name="users-me"),
    path("users", views.UserApiView.as_view(), name="users"),
    path("users/<int:pk>", views.UserApiView.as_view(), name="users-details"),
    path('public', views.public),
    path('private', views.private),
    path('private-scoped', views.private_scoped),
]
