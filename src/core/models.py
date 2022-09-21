from django.db import models
from core.types import AlertStatusType


class Alert(models.Model):
    alert_id = models.CharField(max_length=120)  # Should be unique?
    site = models.CharField(max_length=120)
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
    site = models.CharField(max_length=120)
    subscription = models.CharField(max_length=120)

    amount_billed = models.FloatField(default=0)
    amount_bought = models.FloatField(default=0)

    duration_days = models.IntegerField()
    time = models.DateTimeField()
