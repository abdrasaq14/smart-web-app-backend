from django.db import models
from polymorphic.models import PolymorphicModel
from core.types import AlertStatusType


class ActivityLog(PolymorphicModel):
    alert_id = models.CharField(max_length=120)
    site = models.ForeignKey(
        'core.Site',
        blank=False, null=False,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    zone = models.CharField(max_length=120)
    district = models.CharField(max_length=120)
    activity = models.CharField(max_length=120)
    status = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=AlertStatusType.choices,
        default=AlertStatusType.PENDING.value
    )
    time = models.DateTimeField()


class Alert(ActivityLog):
    def __str__(self) -> str:
        return f"{self.alert_id} - {self.status}"


class EventLog(ActivityLog):
    def __str__(self) -> str:
        return f"{self.alert_id} - {self.status}"


class UserLog(ActivityLog):
    modified_by = models.CharField(max_length=120)
    employee_id = models.CharField(max_length=120)
    email_address = models.CharField(max_length=120)

    def __str__(self) -> str:
        return f"{self.alert_id} - {self.status}"


class TransactionHistory(models.Model):
    site = models.ForeignKey('core.Site', blank=False, null=False, on_delete=models.CASCADE)
    subscription = models.CharField(max_length=120)

    amount_billed = models.FloatField(default=0)
    amount_bought = models.FloatField(default=0)

    duration_days = models.IntegerField()
    time = models.DateTimeField()


class Site(models.Model):
    name = models.CharField(max_length=120)

    asset_name = models.CharField(max_length=240)
    asset_type = models.CharField(max_length=120)
    asset_co_ordinate = models.CharField(max_length=120)
    asset_capacity = models.CharField(max_length=120)

    under_maintenance = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    time = models.DateTimeField()


class Device(models.Model):
    id = models.CharField(max_length=240, unique=True, primary_key=True)

    name = models.CharField(max_length=120)
    location = models.CharField(max_length=240)
    co_ordinate = models.CharField(max_length=240)

    # Should be relation in the future
    company_name = models.CharField(max_length=120)
    company_district = models.CharField(max_length=120)
    company_zone = models.CharField(max_length=120)
    asset_type = models.CharField(max_length=120)
    asset_capacity = models.IntegerField()

    tariff = models.CharField(max_length=120)

    site = models.ForeignKey(
        Site,
        null=False, blank=False,
        on_delete=models.CASCADE,
        related_name='devices'
    )

    linked_at = models.DateTimeField(auto_now_add=True)
