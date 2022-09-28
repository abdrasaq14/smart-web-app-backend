import json
import awswrangler as wr
import numpy as np
import pandas as pd
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from core.models import Alert, Site, TransactionHistory
from core.api.serializers import AlertSerializer, SiteSerializer, TransactionHistorySerializer
from core.pagination import TablePagination
from core.calculations import OrganizationDeviceData
from main import ARC


class OperationsCardsDataApiView(GenericAPIView):
    def get(self, request, **kwargs):
        results = {
            "total_consumption": 0,
            "current_load": 0,
            "avg_availability": 20,
            "power_cuts": 5,
            "overloaded_dts": 10,
            "sites_under_maintenance": Site.objects.filter(under_maintenance=True).count(),
        }

        try:
            results['total_consumption'] = OrganizationDeviceData.get_total_consumption()
            results['current_load'] = OrganizationDeviceData.get_current_load()

        except Exception as e:
            raise e

        return Response(results, status=status.HTTP_200_OK)


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
        response = {
            "dataset": [
                ['district', 'consumption'],
            ]
        }
        df = wr.data_api.rds.read_sql_query(
            sql="SELECT * FROM public.test_table limit 1000",
            con=ARC,
        )
        df['import_active_energy_overall_total'] = df['import_active_energy_overall_total'].astype('float')

        group_by = json.loads(df.groupby('device_model').agg(Sum=('import_active_energy_overall_total', np.sum)).to_json())
        group_by_sum = group_by['Sum']

        for k, v in group_by_sum.items():
            response["dataset"].append([k, v])

        return Response(response, status=status.HTTP_200_OK)


class OperationsSitesApiView(GenericAPIView):
    def get(self, request, **kwargs):
        return Response({
            "total": Site.objects.all().count(),
            "dataset": [
                {"key": 'active', "value": Site.objects.filter(is_active=True).count()},
                {"key": 'offline', "value": Site.objects.filter(is_active=False).count()},
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


class SiteApiView(ListAPIView):
    serializer_class = SiteSerializer
    queryset = Site.objects.all().order_by('time')
    pagination_class = TablePagination
