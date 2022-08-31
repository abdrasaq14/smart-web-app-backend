from django.urls import path
from core.views import WidgetsApiView

urlpatterns = [
    path("widgets/", WidgetsApiView.as_view(), name="widgets-data"),
]
