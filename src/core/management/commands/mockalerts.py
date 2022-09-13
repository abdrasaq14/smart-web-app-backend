from typing import Any

from django.core.management import BaseCommand, CommandParser
from core.models import Alert
from core.tests.factories import AlertFactory


class Command(BaseCommand):
    """
    Create some mock data for alerts. This command is only for dev purpose.

    python src/manage.py mockalerts
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
        created_alerts = []

        if clear:
            Alert.objects.all().delete()

        for i in range(alerts_no):
            alert = AlertFactory()
            created_alerts.append(alert)

        self.stdout.write(f"{len(created_alerts)} alerts generated!")
