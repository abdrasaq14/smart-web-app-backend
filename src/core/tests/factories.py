import factory
from factory.fuzzy import FuzzyDateTime, FuzzyFloat, FuzzyInteger
from datetime import datetime
from pytz import UTC

from core.models import Alert, Site, TransactionHistory
from core.types import AlertStatusType


class SiteFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Site - %s" % n)

    asset_name = factory.Sequence(lambda n: "Asset name - %s" % n)
    asset_type = factory.Sequence(lambda n: "AType - %s" % n)
    asset_co_ordinate = factory.Sequence(lambda n: "#4312SDSA - %s" % n)
    asset_capacity = factory.Sequence(lambda n: "1234 KW - %s" % n)

    time = FuzzyDateTime(datetime(2019, 1, 1, tzinfo=UTC))

    class Meta:
        model = Site


class TransactionHistoryFactory(factory.django.DjangoModelFactory):
    site = factory.SubFactory(SiteFactory)
    subscription = factory.Sequence(lambda n: "Sub - %s" % n)

    amount_billed = FuzzyFloat(0, 99999)
    amount_bought = FuzzyFloat(0, 99999)

    duration_days = FuzzyInteger(0, 10)
    time = FuzzyDateTime(datetime(2019, 1, 1, tzinfo=UTC))

    class Meta:
        model = TransactionHistory


class AlertFactory(factory.django.DjangoModelFactory):
    alert_id = factory.Sequence(lambda n: "ABU-%s" % n)

    site = factory.SubFactory(SiteFactory)

    zone = factory.Sequence(lambda n: "Zone - %s" % n)
    district = factory.Sequence(lambda n: "District - %s" % n)
    activity = factory.Sequence(lambda n: "Activity - %s" % n)
    status = AlertStatusType.PENDING.value
    time = FuzzyDateTime(datetime(2008, 1, 1, tzinfo=UTC))

    class Meta:
        model = Alert
