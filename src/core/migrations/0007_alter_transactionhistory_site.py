# Generated by Django 4.1 on 2022-09-21 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_auto_20220921_1527"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transactionhistory",
            name="site",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="core.site"
            ),
        ),
    ]
