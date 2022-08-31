"""
Settings specifically designed to run on local development
"""
from ..settings import *

DJANGOENV = "development"
DEBUG = True

INSTALLED_APPS += ["django_extensions"]

VERBOSE_LOGGING = False

# CELERY_TASK_ALWAYS_EAGER = True
