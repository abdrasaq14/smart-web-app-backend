# Generated by Django 4.1 on 2022-11-22 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_remove_site_asset_co_ordinate"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="site",
            name="asset_capacity",
        ),
    ]
