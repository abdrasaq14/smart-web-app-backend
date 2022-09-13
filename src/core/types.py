from django.db import models


class AlertStatusType(models.TextChoices):
    COMPLETED = "completed", "Completed"
    PENDING = "pending", "Pending"
    FAILED = "failed", "Failed"
