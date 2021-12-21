"""
Django settings for coriolis project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import socket
from pathlib import Path

import environ
from payments_przelewy24.config import Przelewy24Config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ----- Environment Setup -----

env = environ.Env()
env.read_env(env.str('ENV_PATH', default='.env'))

# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
SECRET_KEY = env.str('SECRET_KEY', 'what-a-horribly-insecure-world-is-this')
ENVIRONMENT = env.str('ENVIRONMENT', 'development')
DEBUG = env.bool('DEBUG', True)

dsn = env.str('SENTRY_DSN', None)
if not DEBUG and dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],
        send_default_pii=env.bool('SENTRY_SEND_PII', True),  # Send user details, etc?
        traces_sample_rate=env.float('SENTRY_SAMPLE_RATE', 1.0),  # Ratio of transactions to monitor for perf issues.
    )

hosts = env.str('ALLOWED_HOSTS', None)
if hosts:
    ALLOWED_HOSTS = [host.strip() for host in hosts.split(',')]

phone_region = env.str('PHONENUMBER_REGION', None)
if phone_region:
    PHONENUMBER_DEFAULT_REGION = phone_region

# Database: https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {'default': env.db()}

# Email: https://django-environ.readthedocs.io/en/latest/tips.html#email-settings
vars().update(env.email('EMAIL_URL', default='consolemail://'))
SERVER_EMAIL = env.str('SERVER_EMAIL', 'coriolis@localhost')
DEFAULT_FROM_EMAIL = SERVER_EMAIL

CURRENCY = env.str('CURRENCY', 'EUR')
TIME_ZONE = env.str('TIME_ZONE', 'Etc/UTC')
LANGUAGE_CODE = env.str('LANGUAGE_CODE', 'en-us')

MEDIA_ROOT = env.str('MEDIA_ROOT', BASE_DIR / 'media')
MEDIA_URL = env.str('MEDIA_URL', '/media/')

# --- STUFF BELOW THIS POINT SHOULD NOT BE CONFIGURABLE PER ENVIRONMENT. ---

if DEBUG:
    import os  # only if you haven't already imported this
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'allauth',
    'allauth.account',

    # do more allauth here...
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.microsoft',
    # 'allauth.socialaccount.providers.twitter',
    # 'allauth.socialaccount.providers.discord',

    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'allauth_2fa',

    'djmoney',
    'payments',
    'payments_przelewy24',

    'colorfield',
    'phonenumber_field',
    'crispy_forms',
    'crispy_bootstrap5',
    'debug_toolbar',

    'events',
]

CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'allauth_2fa.middleware.AllauthTwoFactorMiddleware',
    'events.middleware.RequireSuperuser2FAMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = 'events.User'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_ADAPTER = 'allauth_2fa.adapter.OTPAdapter'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

PAYMENT_CURRENCY = env.str('PAYMENT_CURRENCY', 'XXX')
PAYMENT_USES_SSL = env.bool('PAYMENT_HTTPS', not DEBUG)  # Enforce HTTPS on production envs.
PAYMENT_MODEL = "events.Payment"
PAYMENT_VARIANTS = {
    "default": ("payments.dummy.DummyProvider", {}),
    "przelewy24": (
        "payments_przelewy24.provider.Przelewy24Provider",
        {"config": Przelewy24Config.from_env()},
    ),
}

SITE_ID = 1
ROOT_URLCONF = 'coriolis.urls'
WSGI_APPLICATION = 'coriolis.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'events.context.global_listed_event_pages',
            ],
        },
    },
]

# Password validation: https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# https://docs.djangoproject.com/en/3.2/topics/i18n/
LOCALE_PATHS = [BASE_DIR / 'locale']
USE_I18N = True
USE_L10N = True
USE_TZ = True

# We're using Whitenoise - don't make this configurable.
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# TODO: For Django 4.0 migration, this should be 'static/'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
