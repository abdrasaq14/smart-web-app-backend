from typing import Any

from django.core.management import BaseCommand, CommandParser
from core.models import Alert, TransactionHistory
from core.tests.factories import AlertFactory, TransactionHistoryFactory


class Command(BaseCommand):
    """
    Create some mock data for alerts. This command is only for dev purpose.

    python src/manage.py mock_data
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clear",
            "-c",
            dest="clear",
            help="Clear old alerts",
            type=bool,
            required=False,
            default=False
        )
        parser.add_argument(
            "--number",
            "-n",
            dest="number",
            help="Number of alerts created",
            type=int,
            required=False,
            default=30
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Generate some mock data for Alert model
        """
        clear = options["clear"]
        alerts_no = options["number"]
        generated = {
            'alerts': 0,
            'transaction_history': 0
        }

        if clear:
            Alert.objects.all().delete()
            TransactionHistory.objects.all().delete()

        # Create objects
        for i in range(alerts_no):
            # Alerts
            AlertFactory()
            generated['alerts'] += 1

            # Transaction history
            TransactionHistoryFactory()
            generated['transaction_history'] += 1

        self.stdout.write(f"{generated['alerts']} alerts generated!")
        self.stdout.write(f"{generated['transaction_history']} transaction history objects generated!")
