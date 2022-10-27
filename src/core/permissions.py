from typing import List
import jwt
from rest_framework.permissions import BasePermission

from accounts.utils import get_token_auth_header


class BaseAccountPermission(BasePermission):
    """
    Simple base account permissions.
    """

    access_types = []

    def requires_scope(request, required_scopes: List[str]):
        token = get_token_auth_header(request)
        decoded = jwt.decode(token, verify=False)

        if decoded.get("scope"):
            token_scopes = decoded["scope"].split()
            for token_scope in token_scopes:
                if token_scope in required_scopes:
                    return True

        return False

    def has_permission(self, request, view):
        return self.requires_scope(self.access_types)


class AdminAccessPermission(BaseAccountPermission):
    """Admin access permissions"""
    access_types = ['admin']


class ManagerAccessPermission(BaseAccountPermission):
    """Manager access permissions"""
    access_types = ['admin', 'manager']


class OperationAccessPermission(BaseAccountPermission):
    """Operation access permissions"""
    access_types = ['admin', 'manager', 'operation']


class FinanceAccessPermission(BaseAccountPermission):
    """Finance access permissions"""
    access_types = ['admin', 'manager', 'operation', 'finance']
