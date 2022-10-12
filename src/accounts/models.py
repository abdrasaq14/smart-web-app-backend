from django.contrib.auth import models as auth_models
from django.db import models
from django.utils.translation import gettext_lazy as _
from loguru import logger

from accounts.types import UserLevelAccess
from accounts.utils import assign_user_perm


class User(auth_models.AbstractUser):
    access_level = models.CharField(
        max_length=40,
        null=False,
        blank=False,
        choices=UserLevelAccess.choices,
        default=UserLevelAccess.USER.value,
    )

    email = models.EmailField(_("email address"), blank=True, unique=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        """
        Permissions for the User model table.
        """

        permissions = (
            (UserLevelAccess.ADMIN.value, UserLevelAccess.ADMIN.label),
            (UserLevelAccess.USER.value, UserLevelAccess.USER.label),
        )

    def __str__(self):
        return f"{self.email} - Permission: {self.get_access_level_display()}"

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     if self.access_level == UserLevelAccess.ADMIN.value:
    #         User.assign_user_permission(self, self, UserLevelAccess.ADMIN.value)
    #     else:
    #         User.assign_user_permission(self, self, UserLevelAccess.USER.value)

    #     logger.info(
    #         f"Updating user access level to {self.access_level} for user {self.pk}."
    #     )

    @classmethod
    def assign_user_permission(cls, user, obj, permission, revoke=False):
        """
        Assigns a user to a given permission.

        Args:
            user: User to assign.
            obj: Object to assign to.
            permission: Permission to be assigned.
            revoke: Revoke any permission.
        """
        access_level = (
            UserLevelAccess.ADMIN.value
            if permission == UserLevelAccess.ADMIN.value
            else UserLevelAccess.USER.value
        )
        User.objects.filter(pk=user.pk).update(access_level=access_level)

        # MAKING SURE THAT AN ADMIN IS ADMIN AND NOT GUTTED WITH MORE THAN ONE LIKE USER
        if access_level == UserLevelAccess.ADMIN.value:
            assign_user_perm(UserLevelAccess.USER.value, user, obj, True)

        if access_level == UserLevelAccess.USER.value:
            assign_user_perm(UserLevelAccess.ADMIN.value, user, obj, True)

        assign_user_perm(permission, user, obj, revoke)

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"
