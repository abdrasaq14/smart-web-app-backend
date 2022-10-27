from django.db import models
from django.utils.translation import gettext_lazy as _


class UserLevelAccess(models.TextChoices):
    ADMIN = "admin", _("Admin")
    MANAGER = "manager", _("Manager")
    OPERATION = "operation", _("Operation")
    FINANCE = "finance", _("Finance")
