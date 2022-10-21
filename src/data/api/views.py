from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from core.models import Device, Site
from core.types import AlertStatusType
from core.utils import CompanySiteFiltersMixin
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
class OperationsDashboardRevenueLossApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        revenue_loss = device_data.get_revenue_loss()

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


class OperationsDashboardKeyInsightsApiView(BaseDeviceDataApiView):
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


class OperationsDashboardEnergyChartApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
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


class OperationsDashboardCardsDataApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
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


class OperationsDashboardDTStatusApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        site_data = self.device_data_manager()
        dt_status = site_data.get_dt_status()

        return Response({"dataset": dt_status}, status=status.HTTP_200_OK)


class OperationsDashboardAverageDailyLoadApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        daily_load = device_data.get_daily_load()

        response = {
            "dataset": [
                ['date', 'red_phase', 'yellow_phase', 'blue_phase'],
            ] + daily_load,
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardAverageDailyPFApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        daily_pf = device_data.get_daily_power_factor()

        response = {
            "dataset": [
                ['date', 'red_phase', 'yellow_phase', 'blue_phase'],
            ] + daily_pf,
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardAverageDailyVoltageApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        daily_voltage = device_data.get_daily_voltage()

        response = {
            "dataset": [
                ['date', 'red_phase', 'yellow_phase', 'blue_phase'],
            ] + daily_voltage,
        }

        return Response(response, status=status.HTTP_200_OK)


# Finance Home Data
class FinanceRevenueApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        companies = self.get_companies(request)

        districts = (
            Device.objects.filter(site__in=sites, company__in=companies)
            .values_list("company_district", flat=True)
            .distinct()
        )

        device_data = self.device_data_manager()
        by_district = device_data.get_revenue_by_district(districts)

        response = {
            "dataset": [
                ["district", "revenue"],
            ]
        }

        for k, v in by_district.items():
            response["dataset"].append([k, round(v, 2)])

        return Response(response, status=status.HTTP_200_OK)


class FinancePerformanceApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        data_by = self.request.query_params.get("by", "month")
        if data_by == "month":
            by_dataset = device_data.get_finance_performance_by_month()
        else:
            by_dataset = device_data.get_finance_performance_by_day()

        response = {
            "dataset": [
                ["month", "collection", "billedEnergy"],
            ] + by_dataset,
        }

        return Response(response, status=status.HTTP_200_OK)


class FinanceCustomerBreakdownApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        paying, defaulting = device_data.get_customer_breakdown()

        response = {
            "total": paying + defaulting,
            "dataset": [
                {"key": "paying", "value": paying},
                {"key": "defaulting", "value": defaulting},
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class FinanceCardsDataApiView(BaseDeviceDataApiView):
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        total_revenue = device_data.get_total_revenue_finance()
        avg_availability, power_cuts = device_data.get_avg_availability_and_power_cuts()

        response = {
            "total_revenue": total_revenue,
            "atc_losses": device_data.get_atc_losses(total_revenue),
            "downtime_losses": total_revenue / device_data.get_dt_offline_hours(),
            "tarrif_losses": 29019591,
            "highest_losses": total_revenue / avg_availability,
            "highest_revenue": total_revenue / len(device_data.device_ids),
        }

        return Response(response, status=status.HTTP_200_OK)
