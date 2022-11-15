from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from accounts.models import User
from core.constants import DEFAULT_CACHE_TIME

from core.models import Alert, Device, Site
from core.permissions import AdminAccessPermission, FinanceAccessPermission, ManagerAccessPermission, OperationAccessPermission
from core.types import AlertStatusType
from core.utils import CompanySiteFiltersMixin
from data.calculations import DeviceData


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
    permission_classes = (IsAuthenticated, OperationAccessPermission)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def get(self, request, **kwargs):
        card_type = self.request.query_params.get('card_type', None)
        device_data = self.device_data_manager()
        sites = self.get_sites(request)
        response = {}

        if card_type == 'sites' or not card_type:
            sites_under_maintenance = 0
            for site in sites:
                sites_under_maintenance += site.alerts.filter(
                    status=AlertStatusType.PENDING.value
                ).count()

            response["sites_under_maintenance"] = sites_under_maintenance

        if card_type == 'total_consumption' or not card_type:
            response["total_consumption"] = device_data.get_total_consumption()

        if card_type == 'current_load' or not card_type:
            response["current_load"] = device_data.get_current_load()

        if card_type == 'availability' or not card_type:
            active_power, power_cuts = device_data.get_avg_availability_and_power_cuts()
            response["avg_availability"] = active_power
            response["power_cuts"] = power_cuts

            response["avg_availability"] = device_data.get_total_consumption()

        if card_type == 'overloaded_dts' or not card_type:
            response["overloaded_dts"] = device_data.get_overloaded_dts()

        return Response(response, status=status.HTTP_200_OK)


class OperationsProfileChartApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, OperationAccessPermission)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        profile_chart_dataset = device_data.get_load_profile()

        return Response({"dataset": profile_chart_dataset}, status=status.HTTP_200_OK)


class OperationsPowerConsumptionChartApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, OperationAccessPermission)

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
    permission_classes = (IsAuthenticated, OperationAccessPermission)

    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        dt_active_df = device_data.dt_active()
        dt_inactive_df = device_data.dt_offline()

        return Response(
            {
                "total": len(dt_active_df.index) + len(dt_inactive_df.index),
                "dataset": [
                    {"key": "active", "value": len(dt_active_df.index)},
                    {"key": "offline", "value": len(dt_inactive_df.index)},
                ],
            },
            status=status.HTTP_200_OK,
        )


# Operations Site Dashboard
class OperationsDashboardRevenueLossApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, OperationAccessPermission)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def get(self, request, **kwargs):
        device_data = self.device_data_manager()
        revenue_loss = device_data.get_revenue_loss()

        response = {
            "total": revenue_loss["consumption"],
            "dataset": [
                # {"key": "billing", "value": revenue_loss["total_value"]},
                {"key": "collection", "value": revenue_loss["consumption"]},
                {
                    "key": "downtime",
                    "value": revenue_loss["total_value"] - revenue_loss["consumption"],
                },
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardKeyInsightsApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, OperationAccessPermission)

    def get(self, request, **kwargs):
        sites = self.get_sites(request)
        companies = self.get_companies(request)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        q = Q(site__in=sites, site__company__in=companies)

        if start_date:
            q = q & Q(time__gte=start_date)

        if end_date:
            q = q & Q(time__lte=end_date)

        alerts = Alert.objects.filter(q)[:4]

        response = {"insights": []}
        for alert in alerts:
            response["insights"].append(alert.activity)

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardEnergyChartApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, OperationAccessPermission)

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
    permission_classes = (IsAuthenticated, OperationAccessPermission)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def get(self, request, **kwargs):
        card_type = self.request.query_params.get('card_type', None)
        device_data = self.device_data_manager()
        response = {}

        if card_type == 'availability' or not card_type:
            avg_availability, power_cuts = device_data.get_avg_availability_and_power_cuts()
            response["gridHours"] = avg_availability
            response["noOfOutages"] = power_cuts

        if card_type == 'tariffPlan' or not card_type:
            response["tariffPlan"] = device_data.get_total_consumption()

        if card_type == 'downtime' or not card_type:
            response["downtime"] = device_data.get_current_load()

        if card_type == 'revenuePerHour' or not card_type:
            revenue_per_hour = device_data.get_revenue_per_hour(avg_availability)
            response["revenuePerHour"] = revenue_per_hour

        if card_type == 'untappedRevenue' or not card_type:
            response["untappedRevenue"] = device_data.get_untapped_revenue(avg_availability)

        return Response(response, status=status.HTTP_200_OK)


class OperationsDashboardDTStatusApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, OperationAccessPermission)

    def get(self, request, **kwargs):
        site_data = self.device_data_manager()
        dt_status = site_data.get_dt_status()

        return Response({"dataset": dt_status}, status=status.HTTP_200_OK)


class OperationsDashboardAverageDailyLoadApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, OperationAccessPermission)

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
    permission_classes = (IsAuthenticated, OperationAccessPermission)

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
    permission_classes = (IsAuthenticated, OperationAccessPermission)

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
    permission_classes = (IsAuthenticated, FinanceAccessPermission)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
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
    permission_classes = (IsAuthenticated, FinanceAccessPermission)

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
    permission_classes = (IsAuthenticated, FinanceAccessPermission)

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
    permission_classes = (IsAuthenticated, FinanceAccessPermission)

    # @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def get(self, request, **kwargs):
        card_type = self.request.query_params.get('card_type', None)
        device_data = self.device_data_manager()
        response = {}

        if card_type == 'atc_losses' or not card_type:
            total_revenue = device_data.get_total_revenue_finance()
            response["total_revenue"] = total_revenue
            total_amount, total_revenue = device_data.get_atc_losses(total_revenue)
            response["atc_losses"] = 1 - (total_amount / total_revenue) if total_revenue else 0
            response["total_amount"] = total_amount
            response["total_revenue"] = total_revenue

        if card_type == 'downtime_losses' or not card_type:
            total_revenue = device_data.get_total_revenue_finance()
            offline_hours = device_data.get_dt_offline_hours()
            response["total_revenue"] = total_revenue
            response["downtime_losses"] = total_revenue / (offline_hours if offline_hours > 0 else 1)

        if card_type == 'tarrif_losses' or not card_type:
            response["tarrif_losses"] = device_data.get_tariff_losses()

        if card_type == 'highest_losses' or not card_type:
            total_revenue = device_data.get_total_revenue_finance()
            avg_availability, power_cuts = device_data.get_avg_availability_and_power_cuts()
            response["total_revenue"] = total_revenue
            response["highest_losses"] = total_revenue / (avg_availability if avg_availability > 0 else 1)

        if card_type == 'highest_revenue' or not card_type:
            total_revenue = device_data.get_total_revenue_finance()
            response["total_revenue"] = total_revenue
            response["highest_revenue"] = total_revenue / len(device_data.device_ids)

        return Response(response, status=status.HTTP_200_OK)


# Manager Home
class ManagerHomeCardsDataApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, ManagerAccessPermission)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def get(self, request, **kwargs):
        card_type = self.request.query_params.get('card_type', None)
        device_data = self.device_data_manager()

        sites = self.get_sites(request)
        companies = self.get_companies(request)

        users = User.objects.filter(
            companies__in=companies,
            companies__sites__in=sites
        )
        alerts = Alert.objects.filter(
            site__in=sites,
            site__company__in=companies
        )

        response = {
            "number_of_sites": len(sites),
            "number_of_users": len(users),
            "pending_alerts": len(alerts)
        }

        if card_type == 'revenue_losses' or not card_type:
            total_revenue = device_data.get_total_revenue_finance()
            response["total_revenue"] = total_revenue
            total_amount, total_revenue = device_data.get_atc_losses(total_revenue)
            response["atc_losses"] = 1 - (total_amount / total_revenue) if total_revenue else 0
            response["total_amount"] = total_amount
            response["total_revenue"] = total_revenue

        if card_type == 'total_consumption' or not card_type:
            response["total_consumption"] = device_data.get_total_consumption()

        if card_type == 'current_load' or not card_type:
            response["current_load"] = device_data.get_current_load()

        return Response(response, status=status.HTTP_200_OK)


# Account Home
class AccountHomeCardsDataApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, AdminAccessPermission)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def get(self, request, **kwargs):
        card_type = self.request.query_params.get('card_type', None)
        device_data = self.device_data_manager()

        sites = self.get_sites(request)
        companies = self.get_companies(request)
        users = User.objects.filter(
            companies__in=companies,
            companies__sites__in=sites
        )

        response = {
            "total_energy_expanses": 32727658,
            "total_consumption": device_data.get_total_consumption(),
            "current_load": device_data.get_current_load(),
            "co2_savings": 23,
            "number_of_companies": len(companies),
            "number_of_sites": len(sites),
            "number_of_users": len(users),
        }

        return Response(response, status=status.HTTP_200_OK)


class AccountHomeTopRevenueDataApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, AdminAccessPermission)

    def get(self, request, **kwargs):
        device_data = self.device_data_manager()

        response = {
            "dataset": [
                ['company', 'savings'],
                ['K&C Trios', 850],
                ['Da Vinci Vault', 200],
                ['Love Energy', 300],
                ['Justus Industries', 500],
                ['Kinfe ratings', 800],
            ],
        }

        return Response(response, status=status.HTTP_200_OK)


class AccountHomeTopSavingsDataApiView(BaseDeviceDataApiView):
    permission_classes = (IsAuthenticated, AdminAccessPermission)

    def get(self, request, **kwargs):
        device_data = self.device_data_manager()

        response = {
            "dataset": [
                ['company', 'savings'],
                ['K&C Trios', 850],
                ['Da Vinci Vault', 200],
                ['Love Energy', 300],
                ['Justus Industries', 500],
                ['Kinfe ratings', 800],
            ],
        }

        return Response(response, status=status.HTTP_200_OK)
