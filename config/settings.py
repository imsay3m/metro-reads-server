import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from celery.schedules import crontab
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False")

# Set ALLOWED_HOSTS to prevent Host header attacks
# In production, this should be your actual domain name
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# In production, you would also configure CSRF_TRUSTED_ORIGINS if your
# frontend is on a different domain.
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost").split(",")

# Application definition
INSTALLED_APPS = [
    # Our apps
    "apps.users",
    "apps.books",
    "apps.loans",
    "apps.cards",
    "apps.queues",
    "apps.site_config",
    "apps.academic",
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "django_redis",
    "django_celery_beat",
    "solo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {"default": {}}

if "DATABASE_URL" in os.environ:
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=0,
        ssl_require=True,
    )
else:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASS"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }


# DATABASES = {
#     "default": dj_database_url.config(
#         default="postgres://metro_reads_db_user:Qk61PlyUn7uB0Xg0WEFege3bhGKYPlwA@dpg-d2ab35hr0fns7396iigg-a.singapore-postgres.render.com/metro_reads_db",
#     )
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Whitenoise Storage Configuration for Production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "rest_framework.authentication.BasicAuthentication",
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.FilterSet"],
}


REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:
    # --- Production Configuration (for Render/Railway) ---

    # This single dictionary contains all the necessary options for a secure connection.
    # It will be used by the broker, result backend, and cache.
    REDIS_CONNECTION_OPTIONS = {
        "ssl_cert_reqs": None,  # Tells the client not to require a client-side certificate
    }

    # Celery configuration
    CELERY_BROKER_URL = f"{REDIS_URL}/1"
    CELERY_BROKER_TRANSPORT_OPTIONS = REDIS_CONNECTION_OPTIONS

    CELERY_RESULT_BACKEND = f"{REDIS_URL}/1"
    # THIS IS THE CRITICAL FIX: Use the modern, explicit setting for the result backend
    CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = REDIS_CONNECTION_OPTIONS

    # Django-redis Caching configuration
    CACHE_LOCATION = f"{REDIS_URL}/0"
    CACHE_CONNECTION_OPTIONS = REDIS_CONNECTION_OPTIONS

else:
    # --- Local Development Configuration (Fallback) ---
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")

    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    CACHE_LOCATION = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

    # No SSL options needed for local development
    CELERY_BROKER_TRANSPORT_OPTIONS = {}
    CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {}
    CACHE_CONNECTION_OPTIONS = {}


# --- Caching Configuration ---
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            # This passes the SSL options to the connection pool
            "CONNECTION_POOL_KWARGS": CACHE_CONNECTION_OPTIONS,
        },
    }
}

# --- Celery App Configuration ---
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# --- Celery Beat Schedule ---
CELERY_BEAT_SCHEDULE = {
    "check-expired-queues-every-30-mins": {
        "task": "apps.queues.tasks.check_expired_queues",
        "schedule": crontab(minute="*/30"),
    },
    "send-due-date-reminders-daily": {
        "task": "apps.loans.tasks.send_due_date_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    "calculate-fines-daily": {
        "task": "apps.loans.tasks.calculate_and_notify_fines",
        "schedule": crontab(hour=8, minute=5),
    },
}

# --- EMAIL CONFIGURATION ---
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("MAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("MAIL_PASSWORD")

# Frontend Configuration
FRONTEND_BASE_URL = os.getenv(
    "FRONTEND_BASE_URL", "http://localhost:8000"
)  # Fallback to backend URL
