import awswrangler as wr
from datetime import datetime, timedelta
from typing import List

import pandas as pd

from main import ARC
from core.models import Site
from core.constants import DEVICE_DATE_FORMAT


def get_last_month_date() -> str:
    now = datetime.now()
    last_month = now - timedelta(days=2)
    return last_month.strftime(DEVICE_DATE_FORMAT)


class OrganizationDeviceData:
    sites: List[Site] = []
    start_date = None
    end_date = None
    device_ids: List[str] = []
    devices_query: str = None

    def __init__(self, sites: List[Site] = [], start_date=None, end_date=None) -> None:
        self.sites = sites
        self.start_date = start_date
        self.end_date = end_date

        if not self.start_date:
            self.start_date = get_last_month_date()
        if not self.end_date:
            self.end_date = datetime.now().strftime(DEVICE_DATE_FORMAT)

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

    def get_total_consumption(self) -> float:
        # Total Consumption
        sql_query = f"""
            SELECT AVG(import_active_energy_overall_total) FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
        """

        df = self.read_sql(sql_query)
        return round(df['avg'][0], 2)

    def get_current_load(self) -> float:
        # Current Load (kw)
        sql_query = f"""
            SELECT AVG(active_power_overall_total) FROM public.smart_device_readings
            WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self.devices_query}
        """

        df = self.read_sql(sql_query)
        return round(df['avg'][0], 2)

    def get_overloaded_dts(date=get_last_month_date()) -> float:
        ...


class DeviceRules:

    def dt_active(date):
        # (line_to_neutral_voltage_phase_a AND line_to_neutral_voltage_phase_b AND line_to_neutral_voltage_phase_c <> 0)
        df = wr.data_api.rds.read_sql_query(
            sql=f"""
                SELECT * FROM public.smart_device_readings
                WHERE line_to_neutral_voltage_phase_a != 0 AND line_to_neutral_voltage_phase_b != 0 AND line_to_neutral_voltage_phase_c != 0
                AND date > '{date}'
            """,
            con=ARC,
        )

    def dt_offline():
        ...

    def estimated_tariff():
        ...

    def average_load():
        ...

    def potential_consumption():
        ...

    def dt_capacity():
        ...

