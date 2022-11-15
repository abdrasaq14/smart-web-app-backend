from django.db import models
from polymorphic.models import PolymorphicModel

from core.types import AlertStatusType, CompanyType, ServiceType


class Company(models.Model):
    name = models.CharField(max_length=120)
    company_type = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=CompanyType.choices,
        default=CompanyType.CAR_ENERGY.value,
    )

    service_type = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=ServiceType.choices,
        default=ServiceType.ENERGY_MONITORING.value,
    )

    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    renewal_date = models.DateField()

    users = models.ManyToManyField(
        "accounts.User",
        blank=True,
        related_name='companies'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name}"


class ActivityLog(PolymorphicModel):
    alert_id = models.CharField(max_length=120)
    site = models.ForeignKey(
        "core.Site",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    zone = models.CharField(max_length=120)
    district = models.CharField(max_length=120)
    activity = models.CharField(max_length=120)
    status = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=AlertStatusType.choices,
        default=AlertStatusType.PENDING.value,
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
    email_address = models.EmailField()

    def __str__(self) -> str:
        return f"{self.alert_id} - {self.status}"


class TransactionHistory(models.Model):
    site = models.ForeignKey(
        "core.Site", blank=False, null=False, on_delete=models.CASCADE
    )
    subscription = models.CharField(max_length=120)

    amount_billed = models.FloatField(default=0)
    amount_bought = models.FloatField(default=0)

    days = models.IntegerField()
    time = models.DateTimeField()


class Site(models.Model):
    name = models.CharField(max_length=120)

    company = models.ForeignKey(
        Company,
        null=False, blank=False,
        on_delete=models.CASCADE,
        related_name='sites'
    )

    asset_name = models.CharField(max_length=240)
    asset_type = models.CharField(max_length=120)
    asset_co_ordinate = models.CharField(max_length=120)
    asset_capacity = models.IntegerField(blank=True, null=True, default=0)

    under_maintenance = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    time = models.DateTimeField(auto_now_add=True)


class DeviceTariff(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.FloatField()
    daily_availability = models.TextField()

    def __str__(self) -> str:
        return f"{self.name}: {self.price}"


class Device(models.Model):
    id = models.CharField(max_length=240, unique=True, primary_key=True)

    name = models.CharField(max_length=120)
    location = models.CharField(max_length=240)
    co_ordinate = models.CharField(max_length=240)

    company = models.ForeignKey(
        Company,
        null=False, blank=False,
        on_delete=models.CASCADE
    )

    company_district = models.CharField(max_length=120)
    asset_type = models.CharField(max_length=120)
    asset_capacity = models.IntegerField()

    tariff = models.ForeignKey(
        DeviceTariff, blank=False, null=False, on_delete=models.CASCADE
    )

    site = models.ForeignKey(
        Site, null=False, blank=False, on_delete=models.CASCADE, related_name="devices"
    )

    linked_at = models.DateTimeField(auto_now_add=True)
