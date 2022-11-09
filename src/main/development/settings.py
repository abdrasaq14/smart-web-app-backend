"""
Settings specifically designed to run on local development
"""
from ..settings import *

DJANGOENV = "development"
DEBUG = True

INSTALLED_APPS += ["django_extensions"]

VERBOSE_LOGGING = False

BYPASS_PERMISSIONS = True

# CELERY_TASK_ALWAYS_EAGER = True

AUTHENTICATION_BACKENDS = [
    "guardian.backends.ObjectPermissionBackend",
    # 'django.contrib.auth.backends.ModelBackend',
    # 'accounts.backends.RemoteUserBackend',
    'accounts.backends.BypassAuthBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "COERCE_DECIMAL_TO_STRING": False,
}