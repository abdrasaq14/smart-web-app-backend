from django.urls import path
from core.api.views import (
    AlertApiView, OperationsCardsDataApiView, OperationsPowerConsumptionChartApiView, OperationsProfileChartApiView,
    OperationsSiteMonitoredApiView, SiteApiView, TransactionHistoryApiView
)

urlpatterns = [
    path("alerts/", AlertApiView.as_view(), name="alerts"),
    path("sites/", SiteApiView.as_view(), name="sites"),
    path("transaction-history/", TransactionHistoryApiView.as_view(), name="transaction-history"),

    # Operations
    path("operations/cards-data/", OperationsCardsDataApiView.as_view(), name="operations-cards-data"),
    path("operations/sites-monitored/", OperationsSiteMonitoredApiView.as_view(), name="operations-cards-data"),
    path("operations/profile-chart/", OperationsProfileChartApiView.as_view(), name="operations-profile-chart"),
    path("operations/power-consumption-chart/", OperationsPowerConsumptionChartApiView.as_view(), name="operations-power-chart"),

]
