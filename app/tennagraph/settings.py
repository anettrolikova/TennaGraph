"""
Django settings for tennagraph project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import ast
import os
import datetime

from django.utils.translation import ugettext_lazy as _
from dotenv import load_dotenv
from celery.schedules import schedule
import raven

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to .env file
DOTENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(DOTENV_PATH)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ast.literal_eval(os.environ.get('DEBUG'))

ALLOWED_HOSTS = [item.strip() for item in os.environ.get('ALLOWED_HOSTS').split(',')]

# CORS
# If True, the whitelist will not be used and all origins will be accepted. Defaults to False
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (
#     'google.com',
#     'hostname.example.com',
#     'localhost:8000',
#     '127.0.0.1:9000'
# )

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_prometheus',
    'raven.contrib.django.raven_compat',
    'system',
    'eip',
    'stance',
    'influencer',
    'corsheaders',
    'django_cleanup',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'tennagraph.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '/usr/src/app/html'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tennagraph.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', ''),
        'USER': os.environ.get('DATABASE_USER', ''),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', ''),
        'PORT': os.environ.get('DATABASE_PORT', ''),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGES = [
    ('en', _('English')),
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Tell Django where the project's translation files should be.
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Content chunk splitter settings for splitting text into chunks
# before sending it for text-to-speach on Amazon Polly
CHUNK_MAX_LENGTH = 1500

# Temp directory for file rendering
TMP_DIR = os.path.join(BASE_DIR, 'tmp')

# Static dir where any resources reside
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = STATIC_DIR
STATICFILES_DIRS = [
    os.path.join(STATIC_ROOT, 'resources'),
]

# Admin Creds
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

# Amazon WS settings
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET = os.environ.get('AWS_BUCKET')
AWS_STORAGE_BUCKET_NAME = AWS_BUCKET
S3_FILEPATH = os.environ.get('S3_FILEPATH')
S3_HTTP_PREFIX = os.environ.get('S3_HTTP_PREFIX')
AWS_QUERYSTRING_AUTH = False

# Redis configuration
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

SECRET_KEY = os.environ.get('SECRET_KEY')

# Git Hub
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME')
GITHUB_PASSWORD = os.environ.get('GITHUB_PASSWORD')

# Celery application definition
# http://docs.celeryproject.org/en/v4.1.0/userguide/configuration.html
CELERY_BROKER_URL = "redis://%s:%s" % (REDIS_HOST, REDIS_PORT)
CELERY_RESULT_BACKEND = "redis://%s:%s" % (REDIS_HOST, REDIS_PORT)
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

RUN_BEAT_EVERY_5_MINUTES = 300
RUN_BEAT_EVERY_MINUTE = 60
CELERY_BEAT_SCHEDULE = {
    'fetch_eips_from_official_repo': {
        'task': 'eip.tasks.fetch_eips_from_official_repo',
        'schedule': schedule(run_every=RUN_BEAT_EVERY_MINUTE),
    },
    'fetch_influencers_from_hive_one': {
        'task': 'influencer.tasks.fetch_influencers_from_hive_one',
        'schedule': schedule(run_every=RUN_BEAT_EVERY_MINUTE),
    },
}

# Gunicorn settings
GUNICORN_SERVE_STATIC = ast.literal_eval(os.environ.get('GUNICORN_SERVE_STATIC'))

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'EXCEPTION_HANDLER': 'base.exception_handler.base_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'common',
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=int(os.environ.get('JWT_EXPIRATION_DELTA_DAYS'))),
}

# EMAIL TO SEND FROM EMAIL NOTIFICATIONS
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
EMAIL_PORT = os.environ.get('EMAIL_PORT')

# Logging & Logstash
LOGSTASH_ENABLED = ast.literal_eval(os.environ.get('LOGSTASH_ENABLED'))
LOGSTASH_HOST = os.environ.get('LOGSTASH_HOST')
LOGSTASH_PORT = int(os.environ.get('LOGSTASH_PORT'))

if LOGSTASH_ENABLED:
    LOGGING = {
        'version': 1,
        'handlers': {
            'logstash': {
                'level': 'INFO',
                'class': 'logstash.TCPLogstashHandler',
                'host': LOGSTASH_HOST,
                'port': LOGSTASH_PORT,  # Default value: 5959
                'version': 1,
                # Version of logstash event schema. Default value: 0 (for backward compatibility of the library)
                'message_type': 'django',  # 'type' field in logstash message. Default value: 'logstash'.
                'fqdn': False,  # Fully qualified domain name. Default value: false.
                'tags': ['django.request'],  # list of tags. Default: None.
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['logstash'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    }

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

ADMIN_SITE_HEADER = 'TennaGraph Admin'

# Sentry.io/Raven configuration
# Logging & Logstash
RAVEN_ENABLED = ast.literal_eval(os.environ.get('RAVEN_ENABLED'))
if RAVEN_ENABLED:
    APP_VERSION = open(os.path.join(os.getcwd(), 'VERSION'), 'r').readlines()[0].strip()
    RAVEN_DSN = os.environ.get('RAVEN_DSN')
    RAVEN_CONFIG = {
        'dsn': RAVEN_DSN,
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        # 'release': raven.fetch_git_sha(os.path.dirname(__file__)),
        'release': APP_VERSION,
    }

# Application Environment type
APP_ENV = os.environ.get('APP_ENV')

# Site name & url
SITE_NAME = os.environ.get('SITE_NAME')

# Hive One API Url
HIVE_ONE_API_URL = os.environ.get('HIVE_ONE_API_URL')

