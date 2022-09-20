from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from core.models import Alert, TransactionHistory
from core.api.serializers import AlertSerializer, TransactionHistorySerializer
from core.pagination import TablePagination


class OperationsCardsDataApiView(GenericAPIView):
    def get(self, request, **kwargs):
        return Response({
            "total_consumption": 32727658,
            "current_load": 2727121,
            "avg_availability": 20,
            "power_cuts": 5,
            "overloaded_dts": 10,
            "sites_under_maintenance": 2,
        }, status=status.HTTP_200_OK)


class OperationsProfileChartApiView(GenericAPIView):
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


class OperationsPowerConsumptionChartApiView(GenericAPIView):
    def get(self, request, **kwargs):
        return Response({
            "dataset": [
                ['district', 'consumption'],
                ['District E', 850],
                ['District D', 200],
                ['District C', 300],
                ['District B', 500],
                ['District A', 800]
            ],
        }, status=status.HTTP_200_OK)


class OperationsSitesApiView(GenericAPIView):
    def get(self, request, **kwargs):
        return Response({
            "total": 12000,
            "dataset": [
                {"key": 'active', "value": 40},
                {"key": 'offline', "value": 60},
            ],
        }, status=status.HTTP_200_OK)


class AlertApiView(ListAPIView):
    serializer_class = AlertSerializer
    queryset = Alert.objects.all().order_by('time')
    pagination_class = TablePagination


class TransactionHistoryApiView(ListAPIView):
    serializer_class = TransactionHistorySerializer
    queryset = TransactionHistory.objects.all().order_by('time')
    pagination_class = TablePagination
