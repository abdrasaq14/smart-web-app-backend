from django.urls import path
from data.api.views import (
    OperationsCardsDataApiView, OperationsDashboardCardsDataApiView, OperationsDashboardDTStatusApiView,
    OperationsDashboardEnergyChartApiView, OperationsDashboardKeyInsightsApiView, OperationsDashboardRevenueLossApiView,
    OperationsPowerConsumptionChartApiView, OperationsProfileChartApiView,
    OperationsSiteMonitoredApiView
)

urlpatterns = [
    # Operations Dashboard
    path("operations/cards-data", OperationsCardsDataApiView.as_view(), name="operations-cards-data"),
    path("operations/sites-monitored", OperationsSiteMonitoredApiView.as_view(), name="operations-cards-data"),
    path("operations/profile-chart", OperationsProfileChartApiView.as_view(), name="operations-profile-chart"),
    path("operations/power-consumption-chart", OperationsPowerConsumptionChartApiView.as_view(), name="operations-power-chart"),

    # Operations Site Dashboard
    path("operations-dashboard/revenue-loss", OperationsDashboardRevenueLossApiView.as_view(), name="opd-revenue-loss"),
    path("operations-dashboard/key-insights", OperationsDashboardKeyInsightsApiView.as_view(), name="opd-key-insights"),
    path("operations-dashboard/energy-chart", OperationsDashboardEnergyChartApiView.as_view(), name="opd-energy-chart"),
    path("operations-dashboard/cards-data", OperationsDashboardCardsDataApiView.as_view(), name="opd-cards-data"),
    path("operations-dashboard/dt-status", OperationsDashboardDTStatusApiView.as_view(), name="opd-dt-status"),

]
