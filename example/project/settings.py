"""
Django settings for winners project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

from typing import List

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "_omc6hxq40u11no0uvi&g__lzj2n^4-dk#l#i+7+vgng!-bb^)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS: List[str] = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_stomp",
    "import_export",
    "import_export_stomp",
    "winners",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "author.middlewares.AuthorDefaultBackendMiddleware",
]

ROOT_URLCONF = "winners.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

WSGI_APPLICATION = "winners.wsgi.application"

BROKER_URL = os.environ.get("REDIS_URL", "redis://redis")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis")
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DATABASE_NAME", f"{BASE_DIR}/db.sqlite3"),
        "USER": os.environ.get("DATABASE_USER"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR

# LOGS
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "stomp.py": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


# STOMP SETTINGS
STOMP_LISTENER_CLIENT_ID = os.getenv("STOMP_LISTENER_CLIENT_ID")
STOMP_SERVER_HOST = os.getenv("STOMP_SERVER_HOST")
STOMP_SERVER_PORT = os.getenv("STOMP_SERVER_PORT")
STOMP_SERVER_USER = os.getenv("STOMP_SERVER_USER")
STOMP_SERVER_PASSWORD = os.getenv("STOMP_SERVER_PASSWORD")
STOMP_USE_SSL = bool(eval(os.getenv("STOMP_USE_SSL", "False")))
STOMP_SERVER_VHOST = os.getenv("STOMP_SERVER_VHOST")
STOMP_OUTGOING_HEARTBEAT = os.getenv("STOMP_OUTGOING_HEARTBEAT", 15000)
STOMP_INCOMING_HEARTBEAT = os.getenv("STOMP_INCOMING_HEARTBEAT", 15000)

# AWS STORAGE
IMPORT_EXPORT_STOMP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = "minioadmin"
AWS_SECRET_ACCESS_KEY = "minioadmin"
AWS_DEFAULT_REGION = "us-east-1"
AWS_STORAGE_BUCKET_NAME = "example"
AWS_S3_FILE_OVERWRITE = False
IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST = True

AWS_S3_ENDPOINT_URL = os.getenv(
    "AWS_S3_ENDPOINT_URL",
    "http://127.0.0.1:9000"
    if IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST
    else "http://minio:9000",
)

# DJANGO IMPORT EXPORT STOMP
IMPORT_EXPORT_STOMP_MODELS = {
    "Winner": {"app_label": "winners", "model_name": "Winner"}
}
IMPORT_EXPORT_STOMP_PRESIGNED_POST_EXPIRATION = 600
IMPORT_EXPORT_STOMP_PRESIGNED_FOLDER = "import_export_stomp/"
