from django.urls import path
from core.api.views import (
    AlertApiView, CompanyApiView, CompanyDetailsApiView, DeviceApiView, DeviceTariffApiView, EventLogApiView,
    SiteApiView, TransactionHistoryApiView, UserLogApiView
)

urlpatterns = [
    path("alerts", AlertApiView.as_view(), name="alerts"),
    path("alerts/<int:pk>", AlertApiView.as_view(), name="alerts-details"),
    path("event-logs", EventLogApiView.as_view(), name="event-logs"),
    path("event-logs/<int:pk>", EventLogApiView.as_view(), name="event-logs-details"),
    path("user-logs", UserLogApiView.as_view(), name="user-logs"),
    path("user-logs/<int:pk>", UserLogApiView.as_view(), name="user-logs-details"),

    path("sites", SiteApiView.as_view(), name="sites"),
    path("transaction-history", TransactionHistoryApiView.as_view(), name="transaction-history"),
    path("companies", CompanyApiView.as_view(), name="companies"),
    path("company/<str:pk>", CompanyDetailsApiView.as_view(), name="company-details"),
    path("devices", DeviceApiView.as_view(), name="devices"),
    path("devices/<str:pk>", DeviceApiView.as_view(), name="devices-details"),
    path("device-tariffs", DeviceTariffApiView.as_view(), name="device-tariffs"),
]
