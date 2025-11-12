"""
Django settings for yale_newcomer_survival_guide project.

This file contains all configuration settings for the Django application,
including database, security, static files, and installed apps.
"""

from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
# In production, set this via environment variable DJANGO_SECRET_KEY
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-dev-key-change-in-production-12345')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Allowed hosts for production deployment
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])


# ============================================================================
# APPLICATION DEFINITION
# ============================================================================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'whitenoise.runserver_nostatic',  # WhiteNoise for static files
    
    # Local apps
    'guide',  # Main application for content management
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise middleware (must be after SecurityMiddleware)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'yale_newcomer_survival_guide.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'yale_newcomer_survival_guide.wsgi.application'


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# DuckDB database path - file-backed database
DUCKDB_PATH = config('DUCKDB_PATH', default=str(BASE_DIR / 'db' / 'yale_guide.duckdb'))

# Ensure db directory exists
os.makedirs(os.path.dirname(DUCKDB_PATH), exist_ok=True)

# Try to use django-duckdb, fallback to SQLite if unavailable
# Check if duckdb_backend is available by trying to import it
try:
    import duckdb_backend
    # DuckDB backend is available
    DATABASES = {
        'default': {
            'ENGINE': 'duckdb_backend',
            'NAME': DUCKDB_PATH,
            'OPTIONS': {
                'threads': 1,
            }
        }
    }
except ImportError:
    # Fallback to SQLite if DuckDB backend is not available
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db' / 'db.sqlite3',
        }
    }


# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True


# ============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise configuration for static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================================
# AUTHENTICATION & LOGIN SETTINGS
# ============================================================================

LOGIN_URL = 'guide:login'
LOGIN_REDIRECT_URL = 'guide:home'
LOGOUT_REDIRECT_URL = 'guide:home'

# User role groups
READER_GROUP = 'Reader'
CONTRIBUTOR_GROUP = 'Contributor'
ADMIN_GROUP = 'Admin'

