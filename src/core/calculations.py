from datetime import datetime, timedelta
import awswrangler as wr

from main import ARC


def get_last_month_date() -> str:
    now = datetime.now()
    last_month = now - timedelta(days=2)
    return last_month.strftime('%Y-%m-%d')


class OrganizationDeviceData:

    def get_total_consumption(date=get_last_month_date()) -> float:
        # Total Consumption
        df = wr.data_api.rds.read_sql_query(
            sql=f"""SELECT AVG(import_active_energy_overall_total) FROM public.smart_device_readings
                WHERE date > '{date}'
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

