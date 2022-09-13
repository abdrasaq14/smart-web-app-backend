from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from core.mock_data import OrganizationMockData

from core.models import Alert, TransactionHistory
from core.api.serializers import AlertSerializer, TransactionHistorySerializer, WidgetsSerializer
from core.pagination import TablePagination


class WidgetsApiView(ListAPIView):
    """
    Lists all the projects and allows to create a project as well.
    """
    serializer_class = WidgetsSerializer

    def get(self, request, **kwargs):
        serializer = self.get_serializer_class()({'total_revenue': 1232.324})
        return Response(serializer.data, status=status.HTTP_200_OK)


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
