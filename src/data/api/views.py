from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from data.calculations import DeviceRules, OrganizationDeviceData, OrganizationSiteData
from core.models import Device, Site
from core.types import AlertStatusType
from core.utils import GetSitesMixin


# Operations Dashboard
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
            active_power, power_cuts = org_device_data.get_avg_availability_and_power_cuts()

            results['avg_availability'] = active_power
            results['power_cuts'] = power_cuts

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
            try:
                value = v.iloc[0]
            except AttributeError:
                value = 0

            response["dataset"].append([k, value])

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


# Operations Site Dashboard
class OperationsDashboardRevenueLossApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        site_data = OrganizationSiteData(sites, start_date, end_date)

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


# Finance Home Data
class FinanceRevenueApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "dataset": [
                ['district', 'revenue'],
                ['District E', 850],
                ['District D', 200],
                ['District C', 300],
                ['District B', 500],
                ['District A', 800],
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class FinancePerformanceApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "dataset": [
                ['day', 'collection', 'billedEnergy'],
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
                [24, 24, 13],
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class FinanceCustomerBreakdownApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "total": 720000,
            "dataset": [
                { "key": 'paying', "value": 40 },
                { "key": 'defaulting', "value": 60 },
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class FinanceCardsDataApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        response = {
            "total_revenue": 32727658,
            "atc_losses": 23,
            "downtime_losses": 1019591,
            "tarrif_losses": 29019591,
            "highest_losses": 10000000,
            "highest_revenue": 20000000,
        }

        return Response(response, status=status.HTTP_200_OK)