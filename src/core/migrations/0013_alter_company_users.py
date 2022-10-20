# Generated by Django 4.1 on 2022-10-20 12:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0012_device_company_district"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="users",
            field=models.ManyToManyField(
                null=True, related_name="companies", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
