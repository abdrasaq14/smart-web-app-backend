import factory
from factory.fuzzy import FuzzyDateTime
from datetime import datetime
from pytz import UTC

from core.models import Alert
from core.types import AlertStatusType


class AlertFactory(factory.django.DjangoModelFactory):
    alert_id = factory.Sequence(lambda n: "ABU-%s" % n)
    site = factory.Sequence(lambda n: "Site - %s" % n)
    zone = factory.Sequence(lambda n: "Zone - %s" % n)
    district = factory.Sequence(lambda n: "District - %s" % n)
    activity = factory.Sequence(lambda n: "Activity - %s" % n)
    status = AlertStatusType.PENDING.value
    time = FuzzyDateTime(datetime(2008, 1, 1, tzinfo=UTC))

    class Meta:
        model = Alert
