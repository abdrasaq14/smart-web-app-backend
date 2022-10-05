from django.urls import path
from core.api.views import (
    AlertApiView, SiteApiView, TransactionHistoryApiView
)

urlpatterns = [
    path("alerts", AlertApiView.as_view(), name="alerts"),
    path("sites", SiteApiView.as_view(), name="sites"),
    path("transaction-history", TransactionHistoryApiView.as_view(), name="transaction-history"),
]
