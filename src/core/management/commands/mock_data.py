from typing import Any

from django.core.management import BaseCommand, CommandParser
from core.models import Alert, Device, Site, TransactionHistory
from core.tests.factories import AlertFactory, DeviceFactory, SiteFactory, TransactionHistoryFactory


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
        number = options["number"]
        generated = {
            'alerts': 0,
            'transaction_history': 0,
            'sites': 0,
            'devices': 0
        }

        if clear:
            Alert.objects.all().delete()
            TransactionHistory.objects.all().delete()
            Device.objects.all().delete()
            Site.objects.all().delete()

        # Sites
        site = SiteFactory()
        generated['sites'] += 1

        # Create objects
        for i in range(number):
            # Alerts
            AlertFactory(site=site)
            generated['alerts'] += 1

            # Transaction history
            TransactionHistoryFactory(site=site)
            generated['transaction_history'] += 1

        # Devices
        DeviceFactory(site=site, id='AH19141125')
        generated['devices'] = 1

        for key in generated.keys():
            self.stdout.write(f"{generated[key]} {key} generated!")
