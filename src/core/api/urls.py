from django.urls import path
from core.api.views import AlertApiView, OperationsCardsDataApiView, OrganizationApiView, TransactionHistoryApiView

urlpatterns = [
    path("alerts/", AlertApiView.as_view(), name="alerts"),
    path("operations/cards-data/", OperationsCardsDataApiView.as_view(), name="operations-cards-data"),
    path("transaction-history/", TransactionHistoryApiView.as_view(), name="transaction-history"),
    path("organization-data/", OrganizationApiView.as_view(), name="organization-data"),
]
