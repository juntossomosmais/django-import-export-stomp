import os

from logging import Formatter
from pathlib import Path

from import_export_stomp.apps import ImportExportStompConfig

BASE_DIR = Path(__file__).resolve().parent.parent


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    ImportExportStompConfig.name,
]

SITE_ID = 1

ROOT_URLCONF = "urls"

DEBUG = True

STATIC_URL = "/static/"

SECRET_KEY = "2n6)=vnp8@bu0om9d05vwf7@=5vpn%)97-!d*t4zq1mku%0-@j"

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ),
        },
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASE_SSL_MODE = os.getenv("DATABASE_SSL_MODE")

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DATABASE_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("DATABASE_USER"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": Formatter,
            "format": "%(levelname)-8s [%(asctime)s] %(name)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "": {"level": os.getenv("ROOT_LOG_LEVEL", "INFO"), "handlers": ["console"]},
        "django": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
            "handlers": ["console"],
        },
        "django.request": {
            "level": os.getenv("DJANGO_REQUEST_LOG_LEVEL", "INFO"),
            "handlers": ["console"],
            "propagate": False,
        },
        "django.db.backends": {
            "level": os.getenv("DJANGO_DB_BACKENDS_LOG_LEVEL", "INFO"),
            "propagate": False,
            "handlers": ["console"],
        },
        "stomp.py": {
            "level": os.getenv("STOMP_LOG_LEVEL", "WARNING"),
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


USE_TZ = False
