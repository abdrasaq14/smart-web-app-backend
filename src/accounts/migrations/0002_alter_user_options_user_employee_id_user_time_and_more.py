# Generated by Django 4.1 on 2022-10-20 12:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "permissions": (("superuser", "Super user"), ("operation", "Operation"))
            },
        ),
        migrations.AddField(
            model_name="user",
            name="employee_id",
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="time",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="access_level",
            field=models.CharField(
                choices=[
                    ("superuser", "Super user"),
                    ("operation", "Operation"),
                    ("finance", "Finance"),
                ],
                default="operation",
                max_length=40,
            ),
        ),
    ]