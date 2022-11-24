from datetime import datetime, timedelta
from statistics import mean
from typing import List

import numpy as np
import pandas as pd
from django.db.models import Avg, Count, Q, Sum

from core.constants import DEVICE_DATE_FORMAT
from core.models import Company, Device, Site, TransactionHistory
from data.models import SmartDeviceReadings
from core.exceptions import GenericErrorException


def get_last_month_date() -> str:
    now = datetime.now()
    last_month = now - timedelta(days=2)
    return last_month.strftime(DEVICE_DATE_FORMAT)


class BaseDeviceData:
    companies: List[Company] = []
    sites: List[Site] = []
    start_date = None
    end_date = None
    device_ids: List[str] = []

    def __init__(self, companies: List[Company] = [], sites: List[Site] = [], start_date=None, end_date=None) -> None:
        self.companies = companies
        self.sites = sites
        self.start_date = start_date
        self.end_date = end_date

        if not self.end_date:
            self.end_date = datetime.now().strftime(DEVICE_DATE_FORMAT)
        if not self.start_date:
            default_start_date = datetime.strptime(
                self.end_date, DEVICE_DATE_FORMAT
            ) - timedelta(days=30)
            self.start_date = default_start_date.strftime(DEVICE_DATE_FORMAT)

        self.device_ids = self._devices_from_sites()

    def _devices_from_sites(self) -> List[str]:
        # Extract all devices from our sites
        device_ids = list()
        for company in self.companies:
            company_devices = list(
                Device.objects.filter(
                    site__in=self.sites,
                    company=company
                ).values_list("id", flat=True)
            )
            device_ids = device_ids + company_devices

        if len(device_ids) < 1:
            raise GenericErrorException('No linked devices!')

        device_set = set(device_ids)
        return list(device_set)


class DeviceRules(BaseDeviceData):
    def dt_active(self) -> int:
        q = Q(
            date__gte=self.start_date,
            date__lte=self.end_date,
            gateway_serial__in=self.device_ids,
        )
        q = q & Q(
            ~Q(line_to_neutral_voltage_phase_a=0)
            | ~Q(line_to_neutral_voltage_phase_b=0)
            | ~Q(line_to_neutral_voltage_phase_c=0)
        )

        readings = (
            SmartDeviceReadings.objects.filter(q)
            .values("gateway_serial")
            .annotate(total=Count("gateway_serial"))
            .filter(total__gt=0)
        )

        return pd.DataFrame(readings)

    def dt_offline(self):
        q = Q(
            date__gte=self.start_date,
            date__lte=self.end_date,
            gateway_serial__in=self.device_ids,
            line_to_neutral_voltage_phase_a=0,
            line_to_neutral_voltage_phase_b=0,
            line_to_neutral_voltage_phase_c=0,
        )
        readings = (
            SmartDeviceReadings.objects.filter(q)
            .values("gateway_serial")
            .annotate(total=Count("gateway_serial"))
            .filter(total__gt=0)
        )

        return pd.DataFrame(readings)

    def average_load(self, device_id: str) -> float:
        avg_power_total = SmartDeviceReadings.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date,
            gateway_serial=device_id,
        ).aggregate(avg_power_total=Avg("active_power_overall_total"))

        return avg_power_total["avg_power_total"]


class DeviceData(DeviceRules):
    def get_total_consumption(self) -> float:
        # Total Consumption
        net_device_data = []
        for device_id in self.device_ids:
            readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                )
                .order_by("timestamp")
                .values("import_active_energy_overall_total")
            )

            if not readings:
                continue

            net_device_data.append(
                readings.last()["import_active_energy_overall_total"]
                - readings.first()["import_active_energy_overall_total"]
            )
        return round(np.sum(net_device_data), 2)

    def get_current_load(self) -> float:
        # Current Load (kw)
        device_values = []
        for device_id in self.device_ids:
            real_time_data = (
                SmartDeviceReadings.objects.filter(
                    gateway_serial=device_id
                )
                .order_by("-timestamp")
                .first()
            )

            if not real_time_data:
                continue

            device_values.append(real_time_data.active_power_overall_total)

        return round(np.sum(device_values), 2)

    def get_avg_availability_and_power_cuts(self):
        total_power_cuts = 0
        active_power_list = []

        for device_id in self.device_ids:
            active_time = power_cuts = 0

            q = Q(
                date__gte=self.start_date,
                date__lte=self.end_date,
                gateway_serial=device_id
            )

            if self.start_date == self.end_date:
                q = Q(date=self.start_date, gateway_serial=device_id)

            data_readings = (
                SmartDeviceReadings.objects.filter(q)
                .order_by("timestamp")
                .values(
                    "line_to_neutral_voltage_phase_a",
                    "line_to_neutral_voltage_phase_b",
                    "line_to_neutral_voltage_phase_c",
                    "timestamp",
                )
            )

            for idx, data in enumerate(data_readings):
                try:
                    nxt_data = data_readings[idx + 1]

                    diff_time = nxt_data["timestamp"] - data["timestamp"]
                    diff_seconds = diff_time.total_seconds()

                    if data["timestamp"].day != nxt_data["timestamp"].day:
                        continue

                    if diff_seconds > 3600:
                        continue
                except IndexError:
                    break

                volt_a = data["line_to_neutral_voltage_phase_a"]
                volt_b = data["line_to_neutral_voltage_phase_b"]
                volt_c = data["line_to_neutral_voltage_phase_c"]

                nxt_volt_a = nxt_data["line_to_neutral_voltage_phase_a"]
                nxt_volt_b = nxt_data["line_to_neutral_voltage_phase_b"]
                nxt_volt_c = nxt_data["line_to_neutral_voltage_phase_c"]

                if volt_a != 0 or volt_b != 0 or volt_c != 0 and (
                    nxt_volt_a != 0 or nxt_volt_b != 0 or nxt_volt_c != 0
                ):
                    active_time += diff_seconds
                elif (volt_a == 0 and volt_b == 0 and volt_c == 0) and (
                    nxt_volt_a != 0 or nxt_volt_b != 0 or nxt_volt_c != 0
                ):
                    power_cuts += 1

            total_power_cuts += power_cuts
            active_power_list.append(active_time)

        avg_power_seconds_mean = mean(active_power_list)
        last_date = datetime.strptime(self.end_date, DEVICE_DATE_FORMAT)
        first_date = datetime.strptime(self.start_date, DEVICE_DATE_FORMAT)

        days_range = (last_date - first_date)
        if days_range.days > 0:
            avg_power_seconds_mean = avg_power_seconds_mean / (days_range.days + 1)

        return round(avg_power_seconds_mean / 3600, 2), total_power_cuts

    def get_overloaded_dts(self) -> int:
        overloaded_dts = 0

        for device_id in self.device_ids:
            data_readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                )
                .order_by("timestamp")
                .values("timestamp", "active_power_overall_total")
            )

            if not data_readings:
                continue

            df = pd.DataFrame(data_readings)
            df["results"] = df["active_power_overall_total"] / (
                Device.objects.get(id=device_id).asset_capacity * 0.8
            )
            if not df[df["results"] > 0.75].empty:
                overloaded_dts += 1

        return overloaded_dts

    def get_power_consumption(self, districts: List[str]) -> dict:
        readings = (
            SmartDeviceReadings.objects.filter(
                date__gte=self.start_date,
                date__lte=self.end_date,
                gateway_serial__in=self.device_ids,
            )
            .order_by("-timestamp")
            .values("gateway_serial", "import_active_energy_overall_total")
        )

        by_district = {}

        for device_id in self.device_ids:
            device = Device.objects.get(id=device_id)
            first_value = readings.filter(gateway_serial=device_id).first()
            last_value = readings.filter(gateway_serial=device_id).last()

            if not first_value or not last_value:
                continue

            if device.company_district not in by_district:
                by_district[device.company_district] = 0

            by_district[device.company_district] += (
                first_value["import_active_energy_overall_total"]
                - last_value["import_active_energy_overall_total"]
            )

        return by_district

    def get_load_profile(self):
        daily_chart_dataset = []

        for i in range(0, 24):
            interval_devices_data = 0

            for device_id in self.device_ids:
                device_mean = SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                    timestamp__hour=i
                ).aggregate(active_power_mean=Avg("active_power_overall_total"))

                if device_mean["active_power_mean"]:
                    interval_devices_data += device_mean["active_power_mean"]

            daily_chart_dataset.append([i, interval_devices_data])

        return daily_chart_dataset

    def get_revenue_loss(self) -> dict:
        readings = (
            SmartDeviceReadings.objects.filter(
                date__gte=self.start_date,
                date__lte=self.end_date,
                gateway_serial__in=self.device_ids,
            )
            .order_by("-timestamp")
            .values("timestamp", "gateway_serial", "import_active_energy_overall_total")
        )

        results = {"total_value": 0, "consumption": 0}

        for device_id in self.device_ids:
            device_avg_load = self.average_load(device_id)

            first_entry = readings.filter(gateway_serial=device_id).first()
            last_entry = readings.filter(gateway_serial=device_id).last()

            if not first_entry or not last_entry:
                continue

            date_diff = first_entry["timestamp"] - last_entry["timestamp"]
            number_of_days = date_diff.days if date_diff.days > 0 else 1

            results["total_value"] += device_avg_load * 24 * number_of_days
            results["consumption"] += (
                first_entry["import_active_energy_overall_total"]
                - last_entry["import_active_energy_overall_total"]
            )

        return results

    def get_dt_status(self) -> dict:
        dt_status = {"percentageValue": 0, "humidity": 0, "temperature": 0}

        for device_id in self.device_ids:
            real_time_data = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                )
                .order_by("-timestamp")
                .first()
            )

            if not real_time_data:
                continue

            dt_status[
                "percentageValue"
            ] += real_time_data.active_power_overall_total / (
                Device.objects.get(id=device_id).asset_capacity * 0.8
            ) * 100

            if real_time_data.analog_input_channel_2:
                dt_status["humidity"] += real_time_data.analog_input_channel_2 * 4.108

            if real_time_data.analog_input_channel_1:
                dt_status["temperature"] += real_time_data.analog_input_channel_1 * 1.833

        for key in dt_status.keys():
            dt_status[key] = round((dt_status[key] / len(self.device_ids)), 2)

        return dt_status

    def get_grid_hours(self) -> float:
        grid_hours = 0

        for device_id in self.device_ids:
            active_time = power_cuts = 0

            data_readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                )
                .order_by("timestamp")
                .values(
                    "line_to_neutral_voltage_phase_a",
                    "line_to_neutral_voltage_phase_b",
                    "line_to_neutral_voltage_phase_c",
                    "timestamp",
                )
            )

            for idx, data in enumerate(data_readings):
                try:
                    nxt_data = data_readings[idx + 1]
                except IndexError:
                    break

                volt_a = data["line_to_neutral_voltage_phase_a"]
                volt_b = data["line_to_neutral_voltage_phase_b"]
                volt_c = data["line_to_neutral_voltage_phase_c"]

                nxt_volt_a = nxt_data["line_to_neutral_voltage_phase_a"]
                nxt_volt_b = nxt_data["line_to_neutral_voltage_phase_b"]
                nxt_volt_c = nxt_data["line_to_neutral_voltage_phase_c"]

                diff_time = nxt_data["timestamp"] - data["timestamp"]
                diff_minutes = diff_time.total_seconds() / 60

                if volt_a != 0 or volt_b != 0 or volt_c != 0:
                    active_time += diff_minutes
                elif (volt_a == 0 and volt_b == 0 and volt_c == 0) and (
                    nxt_volt_a != 0 or nxt_volt_b != 0 or nxt_volt_c != 0
                ):
                    power_cuts += 1

            try:
                days_range = (
                    data_readings.last()["timestamp"] - data_readings.first()["timestamp"]
                )
                if days_range.days > 0:
                    active_time = active_time / days_range.days
            except TypeError:
                continue

            grid_hours += active_time / 60

        return grid_hours

    def get_revenue_per_hour(self, avg_availability=None) -> float:
        # Revenue (Total consumption * Tariff Band) divided by the hours of DT active

        if not avg_availability:
            avg_availability = self.get_avg_availability_and_power_cuts()[0]

        net_device_data = []
        for device_id in self.device_ids:
            readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                )
                .order_by("timestamp")
                .values("import_active_energy_overall_total")
            )

            if not readings:
                continue

            net_device_data.append(
                (
                    readings.last()["import_active_energy_overall_total"]
                    - readings.first()["import_active_energy_overall_total"]
                )
                * Device.objects.get(id=device_id).tariff.price
            )
        revenue = round(np.sum(net_device_data), 2)
        if np.isnan(revenue / avg_availability):
            return 0
        return (revenue / avg_availability)

    def get_traffic_plan(self):
        traffic_prices = Device.objects.filter(id__in=self.device_ids).values_list('tariff__price', flat=True)
        return mean(traffic_prices)

    def get_energy_consumption(self):
        by_month = []

        for i in range(1, 13):
            device_sum = 0
            for device_id in self.device_ids:
                q = Q(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    date__month=i,
                    gateway_serial=device_id
                )
                old_entry = SmartDeviceReadings.objects.filter(q).order_by('timestamp').first()
                real_time_entry = SmartDeviceReadings.objects.filter(q).order_by('timestamp').last()

                if not old_entry or not real_time_entry:
                    continue

                device_sum += real_time_entry.import_active_energy_overall_total - old_entry.import_active_energy_overall_total

            by_month.append(device_sum)
        return by_month

    def get_daily_voltage(self):
        return self._average_daily(
            red_phase_key="line_to_neutral_voltage_phase_a",
            yellow_phase_key="line_to_neutral_voltage_phase_b",
            blue_phase_key="line_to_neutral_voltage_phase_c"
        )

    def get_daily_load(self):
        return self._average_daily(
            red_phase_key="active_power_overall_phase_a",
            yellow_phase_key="active_power_overall_phase_b",
            blue_phase_key="active_power_overall_phase_c"
        )

    def get_daily_power_factor(self):
        return self._average_daily(
            red_phase_key="power_factor_overall_phase_a",
            yellow_phase_key="power_factor_overall_phase_b",
            blue_phase_key="power_factor_overall_phase_c"
        )

    def _average_daily(self, red_phase_key, yellow_phase_key, blue_phase_key):
        daily_chart_dataset = []

        for i in range(0, 24):
            red_phase = yellow_phase = blue_phase = 0

            for device_id in self.device_ids:
                voltage_mean = SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                    timestamp__hour=i
                ).aggregate(
                    red_phase_mean=Avg(red_phase_key),
                    yellow_phase_mean=Avg(yellow_phase_key),
                    blue_phase_mean=Avg(blue_phase_key)
                )

                if voltage_mean["red_phase_mean"]:
                    red_phase += voltage_mean["red_phase_mean"]

                if voltage_mean["yellow_phase_mean"]:
                    yellow_phase += voltage_mean["yellow_phase_mean"]

                if voltage_mean["blue_phase_mean"]:
                    blue_phase += voltage_mean["blue_phase_mean"]

            daily_chart_dataset.append([i, red_phase, yellow_phase, blue_phase])

        return daily_chart_dataset

    def get_revenue_by_district(self, districts: List[str]) -> dict:
        readings = (
            SmartDeviceReadings.objects.filter(
                date__gte=self.start_date,
                date__lte=self.end_date,
                gateway_serial__in=self.device_ids,
            )
            .order_by("-timestamp")
            .values("gateway_serial", "import_active_energy_overall_total")
        )

        by_district = {}

        for device_id in self.device_ids:
            device = Device.objects.get(id=device_id)
            first_value = readings.filter(gateway_serial=device_id).first()
            last_value = readings.filter(gateway_serial=device_id).last()

            if not first_value or not last_value:
                continue

            if device.company_district not in by_district:
                by_district[device.company_district] = 0

            by_district[device.company_district] += (
                first_value["import_active_energy_overall_total"]
                - last_value["import_active_energy_overall_total"]
            ) * device.tariff.price

        return by_district

    def get_total_revenue_finance(self):
        readings = (
            SmartDeviceReadings.objects.filter(
                date__gte=self.start_date,
                date__lte=self.end_date,
                gateway_serial__in=self.device_ids,
            )
            .order_by("-timestamp")
            .values("gateway_serial", "import_active_energy_overall_total")
        )

        total_revenue = 0

        for device_id in self.device_ids:
            device = Device.objects.get(id=device_id)
            first_value = readings.filter(gateway_serial=device_id).first()
            last_value = readings.filter(gateway_serial=device_id).last()

            if not first_value or not last_value:
                continue

            total_revenue += (
                first_value["import_active_energy_overall_total"]
                - last_value["import_active_energy_overall_total"]
            ) * device.tariff.price

        return total_revenue

    def get_atc_losses(self, total_revenue=None):
        if not total_revenue:
            total_revenue = self.get_total_revenue_finance()
        total_amount = 0

        for site in self.sites:
            amount = TransactionHistory.objects.filter(
                site=site,
                time__gte=self.start_date,
                time__lte=self.end_date
            ).aggregate(total=Sum("amount_bought"))
            total_amount += amount['total'] if amount['total'] else 0

        return total_amount, total_revenue

    def get_dt_offline_hours(self):
        offline_hours_list = []

        for device_id in self.device_ids:
            offline_time = 0

            data_readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                )
                .order_by("timestamp")
                .values(
                    "line_to_neutral_voltage_phase_a",
                    "line_to_neutral_voltage_phase_b",
                    "line_to_neutral_voltage_phase_c",
                    "timestamp",
                )
            )

            for idx, data in enumerate(data_readings):
                try:
                    nxt_data = data_readings[idx + 1]
                except IndexError:
                    break

                volt_a = data["line_to_neutral_voltage_phase_a"]
                volt_b = data["line_to_neutral_voltage_phase_b"]
                volt_c = data["line_to_neutral_voltage_phase_c"]

                nxt_volt_a = nxt_data["line_to_neutral_voltage_phase_a"]
                nxt_volt_b = nxt_data["line_to_neutral_voltage_phase_b"]
                nxt_volt_c = nxt_data["line_to_neutral_voltage_phase_c"]

                diff_time = nxt_data["timestamp"] - data["timestamp"]
                diff_seconds = diff_time.total_seconds()

                if (volt_a == 0 and volt_b == 0 and volt_c == 0) and (
                    nxt_volt_a == 0 or nxt_volt_b == 0 or nxt_volt_c == 0
                ):
                    offline_time += diff_seconds

            last_date = datetime.strptime(self.end_date, DEVICE_DATE_FORMAT)
            first_date = datetime.strptime(self.start_date, DEVICE_DATE_FORMAT)

            # days_range = (last_date - first_date)
            # if days_range.days > 0:
            #     offline_time = offline_time / (days_range.days + 1)

            offline_hours_list.append(offline_time)

        avg_offline_mean = sum(offline_hours_list)
        return round(avg_offline_mean / 3600, 2)

    def get_customer_breakdown(self) -> float:
        paying = 0
        defaulting = 0

        for device_id in self.device_ids:
            readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    gateway_serial=device_id,
                )
                .order_by("timestamp")
                .values("import_active_energy_overall_total")
            )

            if not readings:
                continue
            diff = readings.last()["import_active_energy_overall_total"] - readings.first()["import_active_energy_overall_total"]
            if diff <= 20:
                paying += 1
            elif diff > 20:
                defaulting += 1

        return paying, defaulting

    def get_finance_performance_by_month(self):
        by_month = []

        for i in range(1, 13):
            month_entry = [i, 0, 0]

            for device_id in self.device_ids:
                device = Device.objects.get(id=device_id)
                amount = TransactionHistory.objects.filter(
                    site=device.site,
                    time__gte=self.start_date,
                    time__lte=self.end_date,
                    time__month=i
                ).aggregate(
                    total_bought=Sum("amount_bought"),
                    total_billed=Sum("amount_billed")
                )

                month_entry[1] += amount['total_bought'] if amount['total_bought'] else 0
                month_entry[2] += amount['total_billed'] if amount['total_billed'] else 0

            by_month.append(month_entry)
        return by_month

    def get_finance_performance_by_day(self):
        by_day = []

        for i in range(1, 32):
            month_entry = [i, 0, 0]

            for device_id in self.device_ids:
                device = Device.objects.get(id=device_id)
                amount = TransactionHistory.objects.filter(
                    site=device.site,
                    time__gte=self.start_date,
                    time__lte=self.end_date,
                    time__day=i
                ).aggregate(
                    total_bought=Sum("amount_bought"),
                    total_billed=Sum("amount_billed")
                )

                month_entry[1] += amount['total_bought'] if amount['total_bought'] else 0
                month_entry[2] += amount['total_billed'] if amount['total_billed'] else 0

            by_day.append(month_entry)
        return by_day

    def get_tariff_losses(self, total_consumption=None):
        # (Estimated Tariff - Tariff Band) * Total Consumption
        avg_start_date = datetime.strptime(self.end_date, DEVICE_DATE_FORMAT) - timedelta(days=30 * 3)

        new_device_data = DeviceData(
            companies=self.companies,
            sites=self.sites,
            start_date=datetime.strftime(avg_start_date, DEVICE_DATE_FORMAT),
            end_date=self.end_date
        )
        # avg_availability, power_cuts = new_device_data.get_avg_availability_and_power_cuts()
        avg_availability, power_cuts = self.get_avg_availability_and_power_cuts()

        if not total_consumption:
            total_consumption = self.get_total_consumption()

        total_tariff = 0
        for device_id in self.device_ids:
            total_tariff += Device.objects.get(id=device_id).tariff.price
        total_tariff_avg = total_tariff / len(self.device_ids)

        return (avg_availability - total_tariff_avg) * total_consumption

    def get_untapped_revenue(self, avg_availability=None):
        if not avg_availability:
            avg_availability, power_cuts = self.get_avg_availability_and_power_cuts()

        return avg_availability * 30 + self.get_tariff_losses(avg_availability)
