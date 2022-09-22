# Generated by Django 4.1 on 2022-09-21 15:38

from django.db import migrations


def clear_db(apps, schema_editor):
    TransactionHistory = apps.get_model('core', 'transactionhistory')
    Alert = apps.get_model('core', 'alert')

    TransactionHistory.objects.all().delete()
    Alert.objects.all().delete()


def do_nothing(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_alter_transactionhistory_site"),
    ]

    operations = [migrations.RunPython(clear_db, do_nothing)]
