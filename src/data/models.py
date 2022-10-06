from django.db import models


class SmartDeviceReadings(models.Model):
    id = models.BigIntegerField(blank=False, null=False, primary_key=True)
    date = models.TextField(blank=True, null=True)
    timestamp = models.TextField(blank=True, null=True)
    gateway_name = models.TextField(blank=True, null=True)
    gateway_model = models.TextField(blank=True, null=True)
    gateway_serial = models.TextField(blank=True, null=True)
    device_name = models.TextField(blank=True, null=True)
    device_serial = models.TextField(blank=True, null=True)
    line_to_neutral_voltage_phase_a = models.FloatField(blank=True, null=True)
    line_to_neutral_voltage_phase_b = models.FloatField(blank=True, null=True)
    line_to_neutral_voltage_phase_c = models.FloatField(blank=True, null=True)
    import_active_energy_overall_total = models.FloatField(blank=True, null=True)
    active_power_overall_total = models.FloatField(blank=True, null=True)
    analog_input_channel_1 = models.FloatField(blank=True, null=True)
    analog_input_channel_2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'smart_device_readings'
