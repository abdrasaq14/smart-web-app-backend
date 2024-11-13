from typing import List
import jwt
from rest_framework.permissions import BasePermission

from accounts.utils import get_token_auth_header


class BaseAccountPermission(BasePermission):
    """
    Simple base account permissions.
    """

    access_types = []

    def requires_scope(self, request, required_scopes: List[str]):
        token = get_token_auth_header(request)
        decoded = jwt.decode(token, verify=False)

        if decoded.get("scope"):
            token_scopes = decoded["scope"].split()
            for token_scope in token_scopes:
                if token_scope in required_scopes:
                    return True

        return False

    def requires_access_level(self, request, required_scopes: List[str]):
        user = request.user
        if user.access_level in required_scopes:
            print("this is user access_level: ", user.access_level, " and this is the required scope: ", required_scopes)
            return True
        return False

    def has_permission(self, request, view):
        return self.requires_access_level(request, self.access_types)


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
