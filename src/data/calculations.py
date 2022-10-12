from datetime import datetime, timedelta
from statistics import mean
from typing import List

import numpy as np
import pandas as pd
from django.db.models import Avg, Count, Q

from core.constants import DEVICE_DATE_FORMAT
from core.models import Device, Site
from data.models import SmartDeviceReadings
from core.exceptions import GenericErrorException


def get_last_month_date() -> str:
    now = datetime.now()
    last_month = now - timedelta(days=2)
    return last_month.strftime(DEVICE_DATE_FORMAT)


class BaseDeviceData:
    sites: List[Site] = []
    start_date = None
    end_date = None
    device_ids: List[str] = []

    def __init__(self, sites: List[Site] = [], start_date=None, end_date=None) -> None:
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
        for site in self.sites:
            device_ids = device_ids + list(site.devices.values_list("id", flat=True))

        if len(device_ids) < 1:
            raise GenericErrorException('No linked devices!')

        return device_ids


class DeviceRules(BaseDeviceData):
    def dt_active(self) -> int:
        q = Q(
            date__gte=self.start_date,
            date__lte=self.end_date,
            device_serial__in=self.device_ids,
        )
        q = q & Q(
            ~Q(line_to_neutral_voltage_phase_a=0)
            | ~Q(line_to_neutral_voltage_phase_b=0)
            | ~Q(line_to_neutral_voltage_phase_c=0)
        )

        readings = (
            SmartDeviceReadings.objects.filter(q)
            .values("device_serial")
            .annotate(total=Count("device_serial"))
            .filter(total__gt=0)
        )

        return pd.DataFrame(readings)

    def dt_offline(self):
        q = Q(
            date__gte=self.start_date,
            date__lte=self.end_date,
            device_serial__in=self.device_ids,
            line_to_neutral_voltage_phase_a=0,
            line_to_neutral_voltage_phase_b=0,
            line_to_neutral_voltage_phase_c=0,
        )
        readings = (
            SmartDeviceReadings.objects.filter(q)
            .values("device_serial")
            .annotate(total=Count("device_serial"))
            .filter(total__gt=0)
        )

        return pd.DataFrame(readings)

    def average_load(self, device_serial: str) -> float:
        avg_power_total = SmartDeviceReadings.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date,
            device_serial=device_serial,
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
                    device_serial=device_id,
                )
                .order_by("timestamp")
                .values("import_active_energy_overall_total")
            )

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
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    device_serial=device_id,
                )
                .order_by("-timestamp")
                .first()
            )

            device_values.append(real_time_data.active_power_overall_total)

        return round(np.sum(device_values), 2)

    def get_avg_availability_and_power_cuts(self):
        total_power_cuts = 0
        active_power_list = [0]

        for device_id in self.device_ids:
            active_time = power_cuts = 0

            data_readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    device_serial=device_id,
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

            days_range = (
                data_readings.last()["timestamp"] - data_readings.first()["timestamp"]
            )
            if days_range.days > 0:
                active_time = active_time / days_range.days

            total_power_cuts += power_cuts
            active_power_list.append(active_time)

        return round(mean(active_power_list) / 60, 2), total_power_cuts

    def get_overloaded_dts(self) -> int:
        overloaded_dts = 0

        for device_id in self.device_ids:
            data_readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    device_serial=device_id,
                )
                .order_by("timestamp")
                .values("timestamp", "active_power_overall_total")
            )

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
                device_serial__in=self.device_ids,
            )
            .order_by("-timestamp")
            .values("device_serial", "import_active_energy_overall_total")
        )

        by_district = {}

        for device_id in self.device_ids:
            device = Device.objects.get(id=device_id)
            first_value = readings.filter(device_serial=device_id).first()
            last_value = readings.filter(device_serial=device_id).last()

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
                    device_serial=device_id,
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
                device_serial__in=self.device_ids,
            )
            .order_by("-timestamp")
            .values("timestamp", "device_serial", "import_active_energy_overall_total")
        )

        results = {"total_value": 0, "consumption": 0}

        for device_serial in self.device_ids:
            device_avg_load = self.average_load(device_serial)

            first_entry = readings.filter(device_serial=device_serial).first()
            last_entry = readings.filter(device_serial=device_serial).last()

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
                    device_serial=device_id,
                )
                .order_by("-timestamp")
                .first()
            )

            dt_status[
                "percentageValue"
            ] += real_time_data.active_power_overall_total / (
                Device.objects.get(id=device_id).asset_capacity * 0.8
            )
            dt_status["humidity"] += real_time_data.analog_input_channel_2 * 4.108
            dt_status["temperature"] += real_time_data.analog_input_channel_1 * 1.833

        for key in dt_status.keys():
            dt_status[key] = round(dt_status[key], 2)

        return dt_status

    def get_grid_hours(self) -> float:
        grid_hours = 0

        for device_id in self.device_ids:
            active_time = power_cuts = 0

            data_readings = (
                SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    device_serial=device_id,
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

            days_range = (
                data_readings.last()["timestamp"] - data_readings.first()["timestamp"]
            )
            if days_range.days > 0:
                active_time = active_time / days_range.days

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
                    device_serial=device_id,
                )
                .order_by("timestamp")
                .values("import_active_energy_overall_total")
            )

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

        for device_id in self.device_ids:
            for i in range(1, 13):
                q = Q(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    date__month=i,
                    device_serial=device_id
                )
                old_entry = SmartDeviceReadings.objects.filter(q).order_by('timestamp').first()
                real_time_entry = SmartDeviceReadings.objects.filter(q).order_by('timestamp').last()

                if not old_entry or not real_time_entry:
                    by_month.append(0)
                    continue

                by_month.append(
                    real_time_entry.import_active_energy_overall_total
                    - old_entry.import_active_energy_overall_total
                )
        return by_month

    def get_daily_voltage(self):
        daily_chart_dataset = []

        for i in range(0, 24):
            red_phase = yellow_phase = blue_phase = 0

            for device_id in self.device_ids:
                voltage_mean = SmartDeviceReadings.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    device_serial=device_id,
                    timestamp__hour=i
                ).aggregate(
                    red_phase_mean=Avg("line_to_neutral_voltage_phase_a"),
                    yellow_phase_mean=Avg("line_to_neutral_voltage_phase_b"),
                    blue_phase_mean=Avg("line_to_neutral_voltage_phase_c")
                )

                if voltage_mean["red_phase_mean"]:
                    red_phase += voltage_mean["red_phase_mean"]

                if voltage_mean["yellow_phase_mean"]:
                    yellow_phase += voltage_mean["yellow_phase_mean"]

                if voltage_mean["blue_phase_mean"]:
                    blue_phase += voltage_mean["blue_phase_mean"]

            daily_chart_dataset.append([i, red_phase, yellow_phase, blue_phase])

        return daily_chart_dataset
