from django.urls import path
from data.api.views import (
    FinanceCardsDataApiView, FinanceCustomerBreakdownApiView, FinancePerformanceApiView, FinanceRevenueApiView,
    OperationsCardsDataApiView, OperationsDashboardAverageDailyLoadApiView, OperationsDashboardAverageDailyPFApiView,
    OperationsDashboardAverageDailyVoltageApiView, OperationsDashboardCardsDataApiView, OperationsSiteMonitoredApiView,
    OperationsDashboardDTStatusApiView, OperationsDashboardEnergyChartApiView, OperationsDashboardKeyInsightsApiView,
    OperationsDashboardRevenueLossApiView, OperationsPowerConsumptionChartApiView, OperationsProfileChartApiView,
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

    path("operations-dashboard/average-daily-voltage", OperationsDashboardAverageDailyVoltageApiView.as_view(), name="opd-daily-voltage"),
    path("operations-dashboard/average-daily-pf", OperationsDashboardAverageDailyPFApiView.as_view(), name="opd-daily-pf"),
    path("operations-dashboard/average-daily-load", OperationsDashboardAverageDailyLoadApiView.as_view(), name="opd-daily-load"),

    # Finance Home
    path("finance/revenue", FinanceRevenueApiView.as_view(), name="finance-revenue"),
    path("finance/performance", FinancePerformanceApiView.as_view(), name="finance-performance"),
    path("finance/customer-breakdown", FinanceCustomerBreakdownApiView.as_view(), name="finance-customer-breakdown"),
    path("finance/cards-data", FinanceCardsDataApiView.as_view(), name="finance-cards-data"),

]
