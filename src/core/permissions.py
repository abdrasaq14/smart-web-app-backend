from typing import List
import jwt
from rest_framework.permissions import BasePermission

from accounts.utils import get_token_auth_header


class BaseAccountPermission(BasePermission):
    """
    Simple base account permissions.
    """

    required_permissions = []

    def requires_scope(self, request, required_scopes: List[str]):
        token = get_token_auth_header(request)
        decoded = jwt.decode(token, verify=False)

        if decoded.get("permissions"):
            token_scopes = decoded["permissions"].split()
            for token_scope in token_scopes:
                if token_scope in required_scopes:
                    return True

        return False

    def requires_access_level(self, request, required_scopes: List[str]):
        user = request.user
        if user.permissions in required_scopes:
            return True
        return False

    def has_permission(self, request, view):
        return self.requires_access_level(request, self.required_permissions)


class AdminAccessPermission(BaseAccountPermission):
    """Admin access permissions"""
    required_permissions = ['admin:access']


class ManagerAccessPermission(BaseAccountPermission):
    """Manager access permissions"""
    required_permissions = ['admin:access', 'manager:access']


class OperationAccessPermission(BaseAccountPermission):
    """Operation access permissions"""
    required_permissions = ['admin:access', 'manager:access', "operation:access"]


class FinanceAccessPermission(BaseAccountPermission):
    """Finance access permissions"""
    required_permissions = ['admin:access', 'manager:access', "operation:access", "finance:access"]
