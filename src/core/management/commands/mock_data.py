import random
from typing import Any

from django.core.management import BaseCommand, CommandParser
from core.models import ActivityLog, Alert, Device, Site, TransactionHistory
from core.tests.factories import AlertFactory, DeviceFactory, EventLogFactory, SiteFactory, TransactionHistoryFactory, UserLogFactory


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
            'user_logs': 0,
            'event_logs': 0,
            'transaction_history': 0,
            'sites': 3,
            'devices': 3
        }

        if clear:
            ActivityLog.objects.all().delete()
            TransactionHistory.objects.all().delete()
            Device.objects.all().delete()
            Site.objects.all().delete()

        # Sites
        site1 = SiteFactory()
        site2 = SiteFactory()
        site3 = SiteFactory()

        # Create objects
        for i in range(number):
            # Alerts
            AlertFactory(site=random.choice([site1, site2, site3]))
            generated['alerts'] += 1

            # Alerts
            EventLogFactory(site=random.choice([site1, site2, site3]))
            generated['event_logs'] += 1
            # Alerts
            UserLogFactory(site=random.choice([site1, site2, site3]))
            generated['user_logs'] += 1

            # Transaction history
            TransactionHistoryFactory(site=random.choice([site1, site2, site3]))
            generated['transaction_history'] += 1

        # Devices
        DeviceFactory(site=site1, id='AH19141125')
        DeviceFactory(site=site2, id='AH19134411')
        DeviceFactory(site=site3, id='AH19141207')

        for key in generated.keys():
            self.stdout.write(f"{generated[key]} {key} generated!")
