from django.db import models


class SmartDeviceReadings(models.Model):
    date = models.DateField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    gateway_name = models.CharField(max_length=255, blank=True, null=True)
    gateway_model = models.CharField(max_length=255, blank=True, null=True)
    gateway_serial = models.CharField(max_length=255, blank=True, null=True)

    device_name = models.CharField(max_length=255, blank=True, null=True)
    device_serial = models.CharField(max_length=255, blank=True, null=True)

    line_to_neutral_voltage_phase_a = models.FloatField(blank=True, null=True)
    line_to_neutral_voltage_phase_b = models.FloatField(blank=True, null=True)
    line_to_neutral_voltage_phase_c = models.FloatField(blank=True, null=True)
    import_active_energy_overall_total = models.FloatField(blank=True, null=True)
    active_power_overall_total = models.FloatField(blank=True, null=True)
    analog_input_channel_1 = models.FloatField(blank=True, null=True)
    analog_input_channel_2 = models.FloatField(blank=True, null=True)

    power_factor_overall_phase_a = models.FloatField(blank=True, null=True)
    power_factor_overall_phase_b = models.FloatField(blank=True, null=True)
    power_factor_overall_phase_c = models.FloatField(blank=True, null=True)
    active_power_overall_phase_a = models.FloatField(blank=True, null=True)
    active_power_overall_phase_b = models.FloatField(blank=True, null=True)
    active_power_overall_phase_c = models.FloatField(blank=True, null=True)
    # id = models.AutoField()

    class Meta:
        managed = False
        db_table = "smart_device_readings"
