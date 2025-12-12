"""
Django settings for Yale Newcomer Survival Guide.

Configuration for Django 4.2 with PostgreSQL (production) or SQLite (local development).
"""

from pathlib import Path
from decouple import config
import os
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# DEBUG: prefer DJANGO_DEBUG, then DEBUG, default False (12-Factor: env-driven)
DEBUG = os.getenv("DJANGO_DEBUG", os.getenv("DEBUG", "False")).lower() == "true"

# SECRET_KEY: Must be set via environment variable in production (12-Factor: env-driven)
# Using decouple for local .env support, but production should use env vars directly
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or config("DJANGO_SECRET_KEY", default="django-insecure-dev-key-change-in-production")

# Warn if using insecure default in production-like environments
if SECRET_KEY == "django-insecure-dev-key-change-in-production" and not DEBUG:
    import warnings
    warnings.warn(
        "SECRET_KEY is using insecure default. Set DJANGO_SECRET_KEY environment variable in production.",
        UserWarning
    )

# ALLOWED_HOSTS: 12-Factor compliant - fully environment-driven
# In production, DJANGO_ALLOWED_HOSTS must be set explicitly
# For local development, allow localhost defaults only if DEBUG=True
allowed_hosts_env = os.getenv("DJANGO_ALLOWED_HOSTS")
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]
elif DEBUG:
    # Local development: allow localhost defaults only when DEBUG=True
    ALLOWED_HOSTS = [
        "127.0.0.1",
        "localhost",
    ]
else:
    # Production: require explicit DJANGO_ALLOWED_HOSTS
    # This will raise ImproperlyConfigured if not set, which is correct for 12-factor
    ALLOWED_HOSTS = []

# Render automatically provides RENDER_EXTERNAL_HOSTNAME; append it if present
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# GA_MEASUREMENT_ID: Google Analytics Measurement ID (12-Factor: env-driven)
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "G-9XJWT2P5LE")

# ============================================================================
# APPLICATION DEFINITION
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'core.apps.CoreConfig',  # Use explicit AppConfig to enable startup hooks
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'core.context_processors.google_analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# On Render, we use Postgres via DATABASE_URL
# Locally, we fall back to SQLite if DATABASE_URL is not set
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True

# ============================================================================
# STATIC FILES
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# DEFAULT PRIMARY KEY
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# AUTHENTICATION & LOGIN
# ============================================================================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# User role groups
READER_GROUP = 'Reader'
CONTRIBUTOR_GROUP = 'Contributor'
ADMIN_GROUP = 'Admin'

# ============================================================================
# LOGGING (12-Factor: Logs to stdout)
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

