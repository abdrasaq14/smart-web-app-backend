import awswrangler as wr
from datetime import datetime, timedelta
from typing import List
import numpy as np

import pandas as pd

from main import ARC
from core.models import Device, Site
from core.constants import DEVICE_DATE_FORMAT, DEVICE_DATETIME_FORMAT


def get_last_month_date() -> str:
    now = datetime.now()
    last_month = now - timedelta(days=2)
    return last_month.strftime(DEVICE_DATE_FORMAT)


class BaseDeviceData:
    sites: List[Site] = []
    start_date = None
    end_date = None
    device_ids: List[str] = []
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
        sql_query = f"""
            SELECT device_serial
            FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
            AND (line_to_neutral_voltage_phase_a != 0 OR line_to_neutral_voltage_phase_b != 0 OR line_to_neutral_voltage_phase_c != 0)
            GROUP BY device_serial
        """

        df = self.read_sql(sql_query)
        return df

    def dt_offline(self):
        sql_query = f"""
            SELECT device_serial
            FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
            AND (line_to_neutral_voltage_phase_a = 0 AND line_to_neutral_voltage_phase_b = 0 AND line_to_neutral_voltage_phase_c = 0)
            GROUP BY device_serial
        """

        df = self.read_sql(sql_query)
        return df

    def estimated_tariff():
        ...

    def average_load():
        ...

    def potential_consumption():
        ...

    def dt_capacity():
        ...


class OrganizationDeviceData(DeviceRules):

    def get_total_consumption(self) -> float:
        # Total Consumption
        sql_query = f"""
            SELECT AVG(import_active_energy_overall_total) FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
        """

        df = self.read_sql(sql_query)
        if df['avg'][0] is None:
            return 0
        return round(df['avg'][0], 2)

    def get_current_load(self) -> float:
        # Current Load (kw)
        sql_query = f"""
            SELECT AVG(active_power_overall_total) FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
        """

        df = self.read_sql(sql_query)
        if df['avg'][0] is None:
            return 0
        return round(df['avg'][0], 2)

    def get_avg_availability_and_power_cuts(self):
        # AVG availability - Sum for active time
        sql_query = f"""
            SELECT timestamp, line_to_neutral_voltage_phase_a, line_to_neutral_voltage_phase_b, line_to_neutral_voltage_phase_c  FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
            ORDER BY timestamp ASC
            LIMIT 10000
        """

        df = self.read_sql(sql_query)
        active_time = inactive_time = 0

        for idx, row in df.iterrows():
            volt_a = row['line_to_neutral_voltage_phase_a']
            volt_b = row['line_to_neutral_voltage_phase_b']
            volt_c = row['line_to_neutral_voltage_phase_c']

            try:
                nxt = df.iloc[[idx + 1]]
            except IndexError:
                break

            nxt_datetime = datetime.strptime(nxt['timestamp'][idx + 1], DEVICE_DATETIME_FORMAT)
            now_datetime = datetime.strptime(row['timestamp'], DEVICE_DATETIME_FORMAT)
            diff_time = nxt_datetime - now_datetime
            diff_minutes = diff_time.total_seconds() / 60

            if volt_a != 0 or volt_b != 0 or volt_c != 0:
                active_time += diff_minutes
            elif volt_a == 0 and volt_b == 0 and volt_c == 0:
                inactive_time += diff_minutes

        return int(active_time / 60), int(inactive_time / 60)

    def get_overloaded_dts(self):
        # count (active_power_overall_total)/DT capacity > 0.75
        overloaded_dts = 0

        for device_id in self.device_ids:
            sql_query = f"""
                SELECT timestamp, active_power_overall_total FROM public.smart_device_readings
                WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial = '{device_id}'
                ORDER BY timestamp ASC
            """
            df = self.read_sql(sql_query)
            df['results'] = df['active_power_overall_total'] / Device.objects.get(id=device_id).asset_capacity
            if not df[df['results'] > 0.75].empty:
                overloaded_dts += 1

        return overloaded_dts

    def get_power_consumption(self, districts: List[str]):
        # net(import_active_energy_overall_total) aggregated across all devices, filtered by district

        sql_query = f"""
            SELECT device_serial, AVG(import_active_energy_overall_total) FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
            GROUP BY device_serial
        """

        df = self.read_sql(sql_query)
        by_district = {}

        for device_serial in self.device_ids:
            device = Device.objects.get(id=device_serial)

            if device.company_district not in by_district:
                by_district[device.company_district] = 0

            device_avg = df.loc[df['device_serial'] == device_serial]['avg']
            if not device_avg.empty:
                by_district[device.company_district] += device_avg

        return by_district

    def get_load_profile(self):
        sql_query = f"""
            SELECT DISTINCT timestamp, active_power_overall_total, device_serial FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
            GROUP BY timestamp, active_power_overall_total, device_serial
            ORDER BY timestamp ASC
        """

        df = self.read_sql(sql_query)

        # Remove some data if we need.
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[df['timestamp'].dt.second.eq(0)]
        # df = df[df['timestamp'].dt.minute.eq(0) & df['timestamp'].dt.second.eq(0)]

        return df, self.device_ids
