"""
Django settings for smarterise project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
import sys
from pathlib import Path

import environ
from corsheaders.defaults import default_headers
# import requests 
# from jose import jwk

# # Fetching Auth0 public key dynamically
# def get_jwks():
#     jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
#     response = requests.get(jwks_url)
#     return response.json()

# # Function to get the key for token verification
# def get_jwk(key_id):
#     jwks = get_jwks()
#     for key in jwks['keys']:
#         if key['kid'] == key_id:
#             return jwk.construct(key)
#     raise Exception("Unable to find the key")
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

os.path.basename(os.path.dirname(BASE_DIR))
sys.path.append(os.path.join(BASE_DIR))

# Environment setup
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

DJANGOENV = os.getenv("DJANGOENV", "production")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY",
    default="django-insecure-%i&m=brb$n22_*c*7ctl-*veg-bqdl&w-(+8ncjb-_5v+fmz+u",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=False)
TESTING = "pytest" in sys.argv[0]

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["127.0.0.1","localhost"])

CORS_ALLOW_HEADERS = default_headers + ("cache-control",)
CORS_ALLOW_ALL_ORIGINS = env.bool('DJANGO_CORS_ALLOW_ALL_ORIGINS', default=False)
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = env.list(
        "DJANGO_CORS_ALLOWED_ORIGINS",
        default=["http://127.0.0.1:3000","http://localhost:3000"],
    )
    
# print("ALLOWED_HOSTS:", ALLOWED_HOSTS)
# print("CORS_ALLOWED_ORIGINS:", CORS_ALLOWED_ORIGINS)
# Application definition

BASE_INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "polymorphic",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "rest_framework",
    "corsheaders",
    "guardian",
    # "django_celery_results",
]

INSTALLED_APPS = [
    "core",
    "accounts",
    "data"
] + BASE_INSTALLED_APPS

AUTHENTICATION_BACKENDS = [
    "guardian.backends.ObjectPermissionBackend",
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.RemoteUserBackend',
    # 'accounts.backends.BypassAuthBackend',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "lib.middleware.loguru.middleware.DjangoLoguruMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    "default": env.db(
        "DJANGO_DEFAULT_DATABASE",
        default="postgres://dbadmin:smarterise@dev-smarterise-cluster.cluster-cc1vuyce9zcm.eu-west-2.rds.amazonaws.com:5432/smartmeters"
    ),
}



# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


APPEND_SLASH = False

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.custom_authentication.CustomJWTAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "COERCE_DECIMAL_TO_STRING": False,
}


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth
AUTH_USER_MODEL = "accounts.User"

BYPASS_AUTH = env.bool("DJANGO_BYPASS_AUTH", default=False)


AWS_ARN_RESOURCE = env.str("AWS_ARN_RESOURCE", "")
AWS_SECRET_ARN = env.str("AWS_SECRET_ARN", "")
AWS_RDS_DATABASE = env.str("AWS_RDS_DATABASE", "smartmeters")


AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
API_IDENTIFIER = os.environ.get('API_IDENTIFIER')
PUBLIC_KEY = None
JWT_ISSUER = None

if AUTH0_DOMAIN:
    JWT_ISSUER = 'https://' + AUTH0_DOMAIN + '/'

SIMPLE_JWT = {
    'ALGORITHM': 'RS256',
    'SIGNING_KEY': '',  # This will be populated dynamically
    'VERIFYING_KEY': '',  # Will fetch the key from Auth0
    'JWK_URL': f'https://{AUTH0_DOMAIN}/.well-known/jwks.json',  # Correct Auth0 JWKS URL
    'AUTH_HEADER_TYPES': ('Bearer',),  # Should be Bearer for standard JWT usage,
    'AUDIENCE': 'https://api.demo.powersmarter.net/',  # Ensure this matches the token's aud field
}

#  'https://dev-mgw72jpas4obd84e.us.auth0.com/.well-known/jwks.json'

print("AUTH0DOMAIN", AUTH0_DOMAIN, SIMPLE_JWT, JWT_ISSUER)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'smart_device_readings_cache',
#     }
# }
