from django.urls import path
from core.api.views import (
    AlertApiView, EventLogApiView, SiteApiView, TransactionHistoryApiView, UserLogApiView
)

urlpatterns = [
    path("alerts", AlertApiView.as_view(), name="alerts"),
    path("event-logs", EventLogApiView.as_view(), name="event-logs"),
    path("user-logs", UserLogApiView.as_view(), name="user-logs"),
    path("sites", SiteApiView.as_view(), name="sites"),
    path("transaction-history", TransactionHistoryApiView.as_view(), name="transaction-history"),
]
