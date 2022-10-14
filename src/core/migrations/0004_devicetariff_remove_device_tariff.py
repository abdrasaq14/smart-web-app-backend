# Generated by Django 4.1 on 2022-10-11 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_activitylog_alert_eventlog_userlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceTariff",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("price", models.FloatField()),
                ("daily_availability", models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name="device",
            name="tariff",
        ),
    ]