from django.db import models
from core.types import AlertStatusType


class Alert(models.Model):
    alert_id = models.CharField(max_length=120)  # Should be unique?
    site = models.ForeignKey('core.Site', blank=False, null=False, on_delete=models.CASCADE)
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

    site = models.ForeignKey(
        Site,
        null=False, blank=False,
        on_delete=models.CASCADE,
        related_name='devices'
    )

    linked_at = models.DateTimeField(auto_now_add=True)
