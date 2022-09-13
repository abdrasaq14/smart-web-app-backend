from django.urls import path
from core.api.views import WidgetsApiView, AlertApiView, OrganizationApiView

urlpatterns = [
    path("widgets/", WidgetsApiView.as_view(), name="widgets-data"),
    path("alerts/", AlertApiView.as_view(), name="alerts"),
    path("organization-data/", OrganizationApiView.as_view(), name="organization-data"),
]
