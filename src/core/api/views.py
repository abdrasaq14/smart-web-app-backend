from typing import List
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from core.exceptions import GenericErrorException

from core.models import Alert, Device, Site, TransactionHistory
from core.api.serializers import AlertSerializer, SiteSerializer, TransactionHistorySerializer
from core.pagination import TablePagination
from core.calculations import DeviceRules, OrganizationDeviceData
from core.types import AlertStatusType


class GetSitesMixin:
    def get_sites(self, request) -> List[Site]:
        sites = request.query_params.get('sites', '')

        if not sites:
            return Site.objects.all()

        site_ids = sites.split(',')
        return self.search_sites(site_ids)

    def search_sites(self, site_ids: List[str]) -> List[Site]:
        sites = []

        for site_id in site_ids:
            try:
                sites.append(Site.objects.get(id=int(site_id)))
            except Site.DoesNotExist:
                raise GenericErrorException(f'Site: {site_id} does not exist')

        return sites


class OperationsCardsDataApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        sites_under_maintenance = 0
        for site in sites:
            sites_under_maintenance += site.alerts.filter(status=AlertStatusType.PENDING.value).count()

        results = {
            "total_consumption": 0,
            "current_load": 0,
            "avg_availability": 0,
            "power_cuts": 0,
            "overloaded_dts": 0,
            "sites_under_maintenance": sites_under_maintenance,
        }

        try:
            org_device_data = OrganizationDeviceData(sites, start_date, end_date)

            results['total_consumption'] = org_device_data.get_total_consumption()
            results['current_load'] = org_device_data.get_current_load()
            active_power, inactive_power = org_device_data.get_avg_availability_and_power_cuts()

            results['avg_availability'] = active_power
            results['power_cuts'] = inactive_power

            results['overloaded_dts'] = org_device_data.get_overloaded_dts()

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


class OperationsPowerConsumptionChartApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        districts = Device.objects.filter(site__in=sites).values_list('company_district', flat=True).distinct()

        org_device_data = OrganizationDeviceData(sites, start_date, end_date)
        by_district = org_device_data.get_power_consumption(districts)

        response = {
            "dataset": [
                ['district', 'consumption'],
            ]
        }

        for k, v in by_district.items():
            response["dataset"].append([k, v.iloc[0]])

        return Response(response, status=status.HTTP_200_OK)


class OperationsSiteMonitoredApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        device_rules = DeviceRules(sites, start_date, end_date)
        dt_active_df = device_rules.dt_active()
        dt_inactive_df = device_rules.dt_offline()

        return Response({
            "total": Site.objects.all().count(),
            "dataset": [
                {"key": 'active', "value": len(dt_active_df.index)},
                {"key": 'offline', "value": len(dt_inactive_df.index)},
            ],
        }, status=status.HTTP_200_OK)


class AlertApiView(ListAPIView, GetSitesMixin):
    serializer_class = AlertSerializer
    queryset = Alert.objects.all().order_by('time')
    pagination_class = TablePagination

    def get_queryset(self):
        q = Q()
        queryset = self.queryset
        sites = self.get_sites(self.request)

        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date and end_date:
            q = Q(time__range=[start_date, end_date])
        elif start_date and end_date is None:
            q = Q(time__gte=start_date)
        elif end_date and start_date is None:
            q = Q(time__lte=end_date)

        if sites:
            q = q & Q(site__in=sites)

        return queryset.filter(q)


class TransactionHistoryApiView(ListAPIView):
    serializer_class = TransactionHistorySerializer
    queryset = TransactionHistory.objects.all().order_by('time')
    pagination_class = TablePagination


class SiteApiView(ListAPIView, GetSitesMixin):
    serializer_class = SiteSerializer
    pagination_class = TablePagination

    def get_queryset(self):
        sites = self.get_sites(self.request)
        return sites.order_by('time')
