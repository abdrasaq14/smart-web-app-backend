from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from core.mock_data import OrganizationMockData

from core.models import Alert, TransactionHistory
from core.api.serializers import AlertSerializer, TransactionHistorySerializer
from core.pagination import TablePagination


class OperationsCardsDataApiView(ListAPIView):
    """
    Lists the cards data for the operations screen
    """

    def get(self, request, **kwargs):
        return Response({
            "totalConsumption": 32727658,
            "currentLoad": 2727121,
            "avgAvailability": 20,
            "powerCuts": 5,
            "overloadedDTs": 10,
            "sitesUnderMaintenance": 2,
        }, status=status.HTTP_200_OK)


class AlertApiView(ListAPIView):
    """
    Lists all alerts
    """
    serializer_class = AlertSerializer
    queryset = Alert.objects.all().order_by('time')
    pagination_class = TablePagination


class OrganizationApiView(GenericAPIView):
    """
    List the data used on the organization page
    """
    def get(self, request):
        data_provider = OrganizationMockData()
        return Response(
            data_provider.get_data(),
            status=status.HTTP_200_OK
        )


class TransactionHistoryApiView(ListAPIView):
    """
    Lists the transaction history
    """
    serializer_class = TransactionHistorySerializer
    queryset = TransactionHistory.objects.all().order_by('time')
    pagination_class = TablePagination
