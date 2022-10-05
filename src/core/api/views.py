from typing import List
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status, filters
from django.db.models import Q
from core.exceptions import GenericErrorException

from core.models import Alert, Device, Site, TransactionHistory
from core.api.serializers import AlertSerializer, SiteSerializer, TransactionHistorySerializer
from core.pagination import TablePagination
from core.calculations import DeviceRules, OrganizationDeviceData
from core.types import AlertStatusType


class HealthCheckView(GenericAPIView):
    def get(self, request, **kwargs):
        return Response(status=status.HTTP_200_OK)


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


class OperationsProfileChartApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        org_device_data = OrganizationDeviceData(sites, start_date, end_date)
        df, device_ids = org_device_data.get_load_profile()
        pivoted_df = df.pivot_table(index="timestamp", columns="device_serial", values="active_power_overall_total")
        pivoted_df = pivoted_df.fillna(0)

        # response = {"dataset": [["day"]]}
        response = {"dataset": []}
        data_dict = []
        # data_dict = [list(pivoted_df.index)]

        for column in device_ids:
            # response['dataset'][0].append(column)
            try:
                data_dict.append(list(pivoted_df[column]))
            except KeyError:
                pass

        response['dataset'] = response['dataset'] + [list(x) for x in zip(*data_dict)]
        return Response(response, status=status.HTTP_200_OK)


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
    filter_backends = [filters.SearchFilter]
    search_fields = ['alert_id', 'zone', 'district', 'activity', 'status', 'time']

    def get_queryset(self):
        q = Q()
        queryset = super().get_queryset()
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


class OperationsDashboardRevenueLossApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "total": 200000,
            "dataset": [
                { "key": 'billing', "value": 60 },
                { "key": 'collection', "value": 20 },
                { "key": 'downtime', "value": 20 },
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardKeyInsightsApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "insights": [
                'DT is overloaded between 9AM and 1PM',
                'Recurring low PF (inspect industrial customers',
                'No power cuts today',
                '98% collection efficiency',
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardEnergyChartApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "dataset": [
                ['month', 'energy'],
                ['JAN', 420],
                ['FEB', 740],
                ['MAR', 600],
                ['APR', 600],
                ['MAY', 500],
                ['JUN', 800],
                ['JUL', 840],
                ['AUG', 400],
                ['SEP', 800],
                ['OCT', 750],
                ['NOV', 890],
                ['DEC', 980],
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardCardsDataApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "gridHours": 32727658,
            "tariffPlan": 23,
            "noOfOutages": 1019591,
            "downtime": 29019591,
            "revenuePerHour": 32271658,
            "untappedRevenue": 832658,
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardDTStatusApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "dataset": { "percentageValue": 70, "humidity": 45, "temperature": 55 },
        }

        return Response(response, status=status.HTTP_200_OK)
