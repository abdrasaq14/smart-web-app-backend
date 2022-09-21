from django.db import migrations
from core.tests.factories import TransactionHistoryFactory


def mock_transactions(apps, schema_editor):
    for i in range(50):
        TransactionHistoryFactory()

def clear_data(apps, schema_editor):
    TransactionHistory = apps.get_model('core', 'transactionhistory')
    TransactionHistory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_transactionhistory"),
    ]

    operations = [
        migrations.RunPython(mock_transactions, clear_data)
    ]
