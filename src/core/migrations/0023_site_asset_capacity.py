# Generated by Django 4.1 on 2022-11-15 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_remove_site_asset_capacity"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="asset_capacity",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]