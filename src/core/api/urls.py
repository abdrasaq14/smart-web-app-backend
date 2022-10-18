from django.urls import path
from core.api.views import (
    AlertApiView, CompanyApiView, DeviceApiView, DeviceTariffApiView, EventLogApiView, SiteApiView, TransactionHistoryApiView, UserLogApiView
)

urlpatterns = [
    path("alerts", AlertApiView.as_view(), name="alerts"),
    path("event-logs", EventLogApiView.as_view(), name="event-logs"),
    path("user-logs", UserLogApiView.as_view(), name="user-logs"),
    path("sites", SiteApiView.as_view(), name="sites"),
    path("transaction-history", TransactionHistoryApiView.as_view(), name="transaction-history"),
    path("companies", CompanyApiView.as_view(), name="companies"),
    path("devices", DeviceApiView.as_view(), name="devices"),
    path("device-tariffs", DeviceTariffApiView.as_view(), name="device-tariffs"),
]
