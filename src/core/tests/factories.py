from datetime import datetime

import factory
from factory.fuzzy import FuzzyDateTime, FuzzyFloat, FuzzyInteger
from pytz import UTC

from core.models import Alert, Device, EventLog, Site, TransactionHistory, UserLog
from core.types import AlertStatusType


class SiteFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Site - %s" % n)

    asset_name = factory.Sequence(lambda n: "Asset name - %s" % n)
    asset_type = factory.Sequence(lambda n: "AType - %s" % n)
    asset_co_ordinate = factory.Sequence(lambda n: "#4312SDSA - %s" % n)
    asset_capacity = factory.Sequence(lambda n: "1234 KW - %s" % n)

    time = FuzzyDateTime(datetime(2022, 9, 12, tzinfo=UTC))

    class Meta:
        model = Site


class TransactionHistoryFactory(factory.django.DjangoModelFactory):
    site = factory.SubFactory(SiteFactory)
    subscription = factory.Sequence(lambda n: "Sub - %s" % n)

    amount_billed = FuzzyFloat(0, 99999)
    amount_bought = FuzzyFloat(0, 99999)

    duration_days = FuzzyInteger(0, 10)
    time = FuzzyDateTime(datetime(2022, 9, 1, tzinfo=UTC))

    class Meta:
        model = TransactionHistory


class BaseActivityLogFactory(factory.django.DjangoModelFactory):
    alert_id = factory.Sequence(lambda n: "ABU-%s" % n)

    site = factory.SubFactory(SiteFactory)

    zone = factory.Sequence(lambda n: "Zone - %s" % n)
    district = factory.Sequence(lambda n: "District - %s" % n)
    activity = factory.Sequence(lambda n: "Activity - %s" % n)
    status = AlertStatusType.PENDING.value
    time = FuzzyDateTime(datetime(2022, 9, 10, tzinfo=UTC))


class AlertFactory(BaseActivityLogFactory):
    class Meta:
        model = Alert


class EventLogFactory(BaseActivityLogFactory):
    class Meta:
        model = EventLog


class UserLogFactory(BaseActivityLogFactory):
    modified_by = factory.Sequence(lambda n: "Modified by - %s" % n)
    employee_id = factory.Sequence(lambda n: "Employee ID: - %s" % n)
    email_address = factory.Sequence(lambda n: "%s@example.com" % n)

    class Meta:
        model = UserLog


class DeviceFactory(factory.django.DjangoModelFactory):
    id = factory.Sequence(lambda n: "DEVICE-ABU-%s" % n)

    site = factory.SubFactory(SiteFactory)

    name = factory.Sequence(lambda n: "Device_%s" % n)
    location = factory.Sequence(lambda n: "Location - %s" % n)
    co_ordinate = factory.Sequence(lambda n: "Co ordinate - %s" % n)

    company_name = factory.Sequence(lambda n: "Company - %s" % n)
    company_district = factory.Sequence(lambda n: "District - %s" % n)
    company_zone = factory.Sequence(lambda n: "Company zone - %s" % n)
    asset_type = factory.Sequence(lambda n: "Asset type - %s" % n)
    asset_capacity = FuzzyInteger(0, 900)

    class Meta:
        model = Device
