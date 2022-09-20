from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from core.mock_data import OrganizationMockData

from core.models import Alert, TransactionHistory
from core.api.serializers import AlertSerializer, TransactionHistorySerializer
from core.pagination import TablePagination


class OperationsCardsDataApiView(ListAPIView):
    def get(self, request, **kwargs):
        return Response({
            "totalConsumption": 32727658,
            "currentLoad": 2727121,
            "avgAvailability": 20,
            "powerCuts": 5,
            "overloadedDTs": 10,
            "sitesUnderMaintenance": 2,
        }, status=status.HTTP_200_OK)


class OperationsProfileChartApiView(ListAPIView):
    def get(self, request, **kwargs):
        return Response({
            "dataset": [
                ['day', 'profile1', 'profile2'],
                [0, 17, 14],
                [2, 15, 13],
                [4, 12, 12],
                [6, 13, 11],
                [8, 14, 12],
                [10, 16, 13],
                [12, 14, 10],
                [14, 20, 12],
                [16, 19, 9],
                [18, 18, 10],
                [20, 17, 11],
                [22, 22, 10],
                [24, 24, 13]
            ],
        }, status=status.HTTP_200_OK)


class AlertApiView(ListAPIView):
    serializer_class = AlertSerializer
    queryset = Alert.objects.all().order_by('time')
    pagination_class = TablePagination


class OrganizationApiView(GenericAPIView):
    def get(self, request):
        data_provider = OrganizationMockData()
        return Response(
            data_provider.get_data(),
            status=status.HTTP_200_OK
        )


class TransactionHistoryApiView(ListAPIView):
    serializer_class = TransactionHistorySerializer
    queryset = TransactionHistory.objects.all().order_by('time')
    pagination_class = TablePagination
