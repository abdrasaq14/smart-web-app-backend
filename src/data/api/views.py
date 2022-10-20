from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from core.models import Device, Site
from core.types import AlertStatusType
from core.utils import GetSitesMixin, CompanySiteFiltersMixin
from data.calculations import DeviceData, DeviceRules


class BaseDeviceDataApiView(GenericAPIView, CompanySiteFiltersMixin):
    def device_data_manager(self) -> DeviceData:
        companies = self.get_companies(self.request)
        sites = self.get_sites(self.request)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)

        device_data = DeviceData(companies, sites, start_date, end_date)
        return device_data


# Operations Dashboard
class OperationsCardsDataApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)

        sites_under_maintenance = 0
        for site in sites:
            sites_under_maintenance += site.alerts.filter(
                status=AlertStatusType.PENDING.value
            ).count()

        results = {
            "total_consumption": 0,
            "current_load": 0,
            "avg_availability": 0,
            "power_cuts": 0,
            "overloaded_dts": 0,
            "sites_under_maintenance": sites_under_maintenance,
        }

        try:
            device_data = self.device_data_manager()

            (
                active_power,
                power_cuts,
            ) = device_data.get_avg_availability_and_power_cuts()
            results["avg_availability"] = active_power
            results["power_cuts"] = power_cuts
            results["total_consumption"] = device_data.get_total_consumption()
            results["current_load"] = device_data.get_current_load()
            results["overloaded_dts"] = device_data.get_overloaded_dts()

        except Exception as e:
            raise e

        return Response(results, status=status.HTTP_200_OK)


class OperationsProfileChartApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        profile_chart_dataset = device_data.get_load_profile()

        return Response({"dataset": profile_chart_dataset}, status=status.HTTP_200_OK)


class OperationsPowerConsumptionChartApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        companies = self.get_companies(request)

        districts = (
            Device.objects.filter(site__in=sites, company__in=companies)
            .values_list("company_district", flat=True)
            .distinct()
        )

        device_data = self.device_data_manager()
        by_district = device_data.get_power_consumption(districts)

        response = {
            "dataset": [
                ["district", "consumption"],
            ]
        }

        for k, v in by_district.items():
            response["dataset"].append([k, round(v, 2)])

        return Response(response, status=status.HTTP_200_OK)


class OperationsSiteMonitoredApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        dt_active_df = device_data.dt_active()
        dt_inactive_df = device_data.dt_offline()

        return Response(
            {
                "total": Site.objects.all().count(),
                "dataset": [
                    {"key": "active", "value": len(dt_active_df.index)},
                    {"key": "offline", "value": len(dt_inactive_df.index)},
                ],
            },
            status=status.HTTP_200_OK,
        )


# Operations Site Dashboard
class OperationsDashboardRevenueLossApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        site_data = DeviceData(sites, start_date, end_date)
        revenue_loss = site_data.get_revenue_loss()

        response = {
            "total": revenue_loss["total_value"] + revenue_loss["consumption"],
            "dataset": [
                {"key": "billing", "value": revenue_loss["total_value"]},
                {"key": "collection", "value": revenue_loss["consumption"]},
                {
                    "key": "downtime",
                    "value": revenue_loss["total_value"] - revenue_loss["consumption"],
                },
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardKeyInsightsApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        response = {
            "insights": [
                "DT is overloaded between 9AM and 1PM",
                "Recurring low PF (inspect industrial customers",
                "No power cuts today",
                "98% collection efficiency",
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardEnergyChartApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        device_data = DeviceData(sites, start_date, end_date)
        by_month = device_data.get_energy_consumption()

        response = {
            "dataset": [
                ["month", "energy"],
                ["JAN", by_month[0]],
                ["FEB", by_month[1]],
                ["MAR", by_month[2]],
                ["APR", by_month[3]],
                ["MAY", by_month[4]],
                ["JUN", by_month[5]],
                ["JUL", by_month[6]],
                ["AUG", by_month[7]],
                ["SEP", by_month[8]],
                ["OCT", by_month[9]],
                ["NOV", by_month[10]],
                ["DEC", by_month[11]],
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardCardsDataApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        device_data = DeviceData(sites, start_date, end_date)
        avg_availability, power_cuts = device_data.get_avg_availability_and_power_cuts()
        revenue_per_hour = device_data.get_revenue_per_hour(avg_availability)

        response = {
            "gridHours": avg_availability,
            "tariffPlan": device_data.get_total_consumption(),
            "noOfOutages": power_cuts,
            "downtime": device_data.get_current_load(),
            "revenuePerHour": revenue_per_hour,
            "untappedRevenue": 0,
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardDTStatusApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        site_data = DeviceData(sites, start_date, end_date)
        dt_status = site_data.get_dt_status()

        return Response({"dataset": dt_status}, status=status.HTTP_200_OK)


class OperationsDashboardAverageDailyLoadApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        device_data = DeviceData(sites, start_date, end_date)
        daily_load = device_data.get_daily_load()

        response = {
            "dataset": [
                ['date', 'red_phase', 'yellow_phase', 'blue_phase'],
            ] + daily_load,
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardAverageDailyPFApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        device_data = DeviceData(sites, start_date, end_date)
        daily_pf = device_data.get_daily_power_factor()

        response = {
            "dataset": [
                ['date', 'red_phase', 'yellow_phase', 'blue_phase'],
            ] + daily_pf,
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardAverageDailyVoltageApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        device_data = DeviceData(sites, start_date, end_date)
        daily_voltage = device_data.get_daily_voltage()

        response = {
            "dataset": [
                ['date', 'red_phase', 'yellow_phase', 'blue_phase'],
            ] + daily_voltage,
        }

        return Response(response, status=status.HTTP_200_OK)


# Finance Home Data
class FinanceRevenueApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        response = {
            "dataset": [
                ["district", "revenue"],
                ["District E", 850],
                ["District D", 200],
                ["District C", 300],
                ["District B", 500],
                ["District A", 800],
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class FinancePerformanceApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        response = {
            "dataset": [
                ["day", "collection", "billedEnergy"],
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
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        response = {
            "total": 720000,
            "dataset": [
                {"key": "paying", "value": 288000},
                {"key": "defaulting", "value": 432000},
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class FinanceCardsDataApiView(GenericAPIView, GetSitesMixin):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        response = {
            "total_revenue": 32727658,
            "atc_losses": 23,
            "downtime_losses": 1019591,
            "tarrif_losses": 29019591,
            "highest_losses": 10000000,
            "highest_revenue": 20000000,
        }

        return Response(response, status=status.HTTP_200_OK)
