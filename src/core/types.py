from django.db import models


class AlertStatusType(models.TextChoices):
    COMPLETED = "completed", "Completed"
    PENDING = "pending", "Pending"
    FAILED = "failed", "Failed"


class CompanyType(models.TextChoices):
    CAR_ENERGY = "car_energy", "Car Energy"


class ServiceType(models.TextChoices):
    ENERGY_MONITORING = "energy_monitoring", "Energy monitoring"
