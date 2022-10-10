import numpy as np
import pandas as pd
import awswrangler as wr

from typing import List
from datetime import datetime, timedelta
from django.db.models import Avg, Q, Count

from data.models import SmartDeviceReadings

from main import ARC
from core.models import Device, Site
from core.constants import DAYS_IN_MONTH, DEVICE_DATE_FORMAT, DEVICE_DATETIME_FORMAT


def get_last_month_date() -> str:
    now = datetime.now()
    last_month = now - timedelta(days=2)
    return last_month.strftime(DEVICE_DATE_FORMAT)


class BaseDeviceData:
    sites: List[Site] = []
    start_date = None
    end_date = None
    device_ids: List[str] = []
    # DEPRECATED
    devices_query: str = None

    def __init__(self, sites: List[Site] = [], start_date=None, end_date=None) -> None:
        self.sites = sites
        self.start_date = start_date
        self.end_date = end_date

        if not self.end_date:
            self.end_date = datetime.now().strftime(DEVICE_DATE_FORMAT)
        if not self.start_date:
            default_start_date = datetime.strptime(self.end_date, DEVICE_DATE_FORMAT) - timedelta(days=30)
            self.start_date = default_start_date.strftime(DEVICE_DATE_FORMAT)

        self.device_ids = self._devices_from_sites()
        self.devices_query = self._devices_for_query()

    def _devices_from_sites(self) -> List[str]:
        # Extract all devices from our sites
        device_ids = list()
        for site in self.sites:
            device_ids = device_ids + list(site.devices.values_list('id', flat=True))
        return device_ids

    def _devices_for_query(self) -> str:
        if len(self.device_ids) > 1:
            return tuple(self.device_ids)
        return f"('{self.device_ids[0]}')"

    def read_sql(self, sql_query) -> pd.DataFrame:
        print(sql_query)
        return wr.data_api.rds.read_sql_query(sql=sql_query, con=ARC)


class DeviceRules(BaseDeviceData):

    def dt_active(self) -> int:
        q = Q(date__gte=self.start_date, date__lte=self.end_date, device_serial__in=self.device_ids)
        q = q & Q(
            ~Q(line_to_neutral_voltage_phase_a=0)
            | ~Q(line_to_neutral_voltage_phase_b=0)
            | ~Q(line_to_neutral_voltage_phase_c=0)
        )

        readings = SmartDeviceReadings.objects.filter(q).values(
            'device_serial').annotate(
                total=Count('device_serial')).filter(total__gt=0)

        return pd.DataFrame(readings)

    def dt_offline(self):
        q = Q(
            date__gte=self.start_date,
            date__lte=self.end_date,
            device_serial__in=self.device_ids,
            line_to_neutral_voltage_phase_a=0,
            line_to_neutral_voltage_phase_b=0,
            line_to_neutral_voltage_phase_c=0
        )
        readings = SmartDeviceReadings.objects.filter(q).values(
            'device_serial').annotate(
                total=Count('device_serial')).filter(total__gt=0)

        return pd.DataFrame(readings)

    def estimated_tariff():
        ...

    def average_load(self) -> float:
        sql_query = f"""
            SELECT AVG(active_power_overall_total) FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
        """

        df = self.read_sql(sql_query)

        try:
            return df.iloc[0]
        except AttributeError:
            return 0

    def potential_consumption():
        ...

    def dt_capacity():
        ...


class OrganizationDeviceData(DeviceRules):

    def get_total_consumption(self) -> float:
        # Total Consumption
        net_device_data = []
        for device_id in self.device_ids:
            readings = SmartDeviceReadings.objects.filter(
                date__gte=self.start_date,
                date__lte=self.end_date,
                device_serial=device_id
            ).order_by('timestamp').values('import_active_energy_overall_total')

            net_device_data.append(
                readings.last()['import_active_energy_overall_total'] -
                readings.first()['import_active_energy_overall_total']
            )
        return round(np.sum(net_device_data), 2)

    def get_current_load(self) -> float:
        # Current Load (kw)
        device_values = []
        for device_id in self.device_ids:
            real_time_data = SmartDeviceReadings.objects.filter(
                date__gte=self.start_date,
                date__lte=self.end_date,
                device_serial=device_id
            ).order_by('-timestamp').first()

            device_values.append(real_time_data.active_power_overall_total)

        return round(np.sum(device_values), 2)

    def get_avg_availability_and_power_cuts(self):
        active_time = power_cuts = 0

        data_readings = SmartDeviceReadings.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date,
            device_serial__in=self.device_ids
        ).order_by('timestamp').values(
            'line_to_neutral_voltage_phase_a',
            'line_to_neutral_voltage_phase_b',
            'line_to_neutral_voltage_phase_c',
            'timestamp'
        )

        for idx, data in enumerate(data_readings):
            try:
                nxt_data = data_readings[idx + 1]
            except IndexError:
                break

            volt_a = data['line_to_neutral_voltage_phase_a']
            volt_b = data['line_to_neutral_voltage_phase_b']
            volt_c = data['line_to_neutral_voltage_phase_c']

            nxt_volt_a = nxt_data['line_to_neutral_voltage_phase_a']
            nxt_volt_b = nxt_data['line_to_neutral_voltage_phase_b']
            nxt_volt_c = nxt_data['line_to_neutral_voltage_phase_c']

            diff_time = nxt_data['timestamp'] - data['timestamp']
            diff_minutes = diff_time.total_seconds() / 60

            if volt_a != 0 or volt_b != 0 or volt_c != 0:
                active_time += diff_minutes
            elif (volt_a == 0 and volt_b == 0 and volt_c == 0) and (nxt_volt_a != 0 or nxt_volt_b != 0 or nxt_volt_c != 0):
                power_cuts += 1

        days_range = data_readings.last()['timestamp'] - data_readings.first()['timestamp']
        if days_range.days > 0:
            active_time = active_time / days_range.days
        return round(active_time / 60, 2), power_cuts

    def get_overloaded_dts(self):
        overloaded_dts = 0

        for device_id in self.device_ids:
            data_readings = SmartDeviceReadings.objects.filter(
                date__gte=self.start_date,
                date__lte=self.end_date,
                device_serial=device_id
            ).order_by('timestamp').values('timestamp', 'active_power_overall_total')

            df = pd.DataFrame(data_readings)
            df['results'] = df['active_power_overall_total'] / Device.objects.get(id=device_id).asset_capacity * 0.8
            if not df[df['results'] > 0.75].empty:
                overloaded_dts += 1

        return overloaded_dts

    def get_power_consumption(self, districts: List[str]):
        readings = SmartDeviceReadings.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date,
            device_serial__in=self.device_ids
        ).order_by('-timestamp').values('device_serial', 'import_active_energy_overall_total')

        by_district = {}

        for device_id in self.device_ids:
            device = Device.objects.get(id=device_id)
            first_value = readings.filter(device_serial=device_id).first()
            last_value = readings.filter(device_serial=device_id).last()

            if device.company_district not in by_district:
                by_district[device.company_district] = 0

            by_district[device.company_district] += first_value['import_active_energy_overall_total'] - last_value['import_active_energy_overall_total']

        return by_district

    def get_load_profile(self):
        readings = SmartDeviceReadings.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date,
            device_serial__in=self.device_ids
        ).order_by('timestamp').values('timestamp', 'active_power_overall_total', 'device_serial').distinct()

        df = pd.DataFrame(readings)
        # Parse date
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        profile_chart_dataset = []
        minutes_intervals = [[0, 14], [15, 29], [30, 44], [45, 59]]

        for i in range(0, 24):
            # Filter by hour and minute interval
            for minute_interval in minutes_intervals:
                interval_devices_data = 0
                for device_id in self.device_ids:
                    device_df = df[df['device_serial'] == device_id]
                    device_df = device_df[device_df['timestamp'].dt.hour == i]
                    device_df = device_df[device_df['timestamp'].dt.minute >= minute_interval[0]]
                    device_df = device_df[device_df['timestamp'].dt.minute <= minute_interval[1]]

                    avg_df = device_df[['active_power_overall_total']].mean(skipna=True)

                    if not avg_df.isnull().values.any():
                        interval_devices_data += avg_df[0]

                profile_chart_dataset.append(
                    [i, f"{minute_interval[0]}-{minute_interval[1]}", interval_devices_data]
                )

        return profile_chart_dataset


class OrganizationSiteData(DeviceRules):

    def get_revenue_loss(self):
        sql_query = f"""
            SELECT AVG(active_power_overall_total) FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
        """

        df = self.read_sql(sql_query)

        avg_load = self.average_load()
        value = avg_load * 24 * DAYS_IN_MONTH

        
