import awswrangler as wr
from datetime import datetime, timedelta
from typing import List

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

    def __init__(self, sites: List[Site] = [], start_date=None, end_date=None) -> None:
        self.sites = sites
        if not start_date:
            start_date = get_last_month_date()
        if not end_date:
            end_date = datetime.now().strftime(DEVICE_DATE_FORMAT)

    def _devices_from_sites(self) -> str:
        # Extract all devices from our sites
        devices_ids = ()
        for site in self.sites:
            devices = site.devices.all()

        return ('')

    def get_total_consumption(self) -> float:
        # Total Consumption
        devices = self._devices_from_sites()
        df = wr.data_api.rds.read_sql_query(
            sql=f"""SELECT AVG(import_active_energy_overall_total) FROM public.smart_device_readings
                WHERE date > '{self.start_date}' AND date < '{self.end_date}' AND device_serial IN {self._devices_from_sites}
            """,
            con=ARC,
        )
        return df['avg'][0]

    def get_current_load(date=get_last_month_date()) -> float:
        # Current Load (kw)
        df = wr.data_api.rds.read_sql_query(
            sql=f"SELECT AVG(active_power_overall_total) FROM public.smart_device_readings WHERE date > '{date}'",
            con=ARC,
        )
        return df['avg'][0]

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

