#!/usr/bin/env python
"""
Verify environment variables are loading correctly.

This script checks the environment variables that settings.py actually uses.
"""
import os
import sys

# Setup Django to verify actual settings values
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Check raw environment variables first
print("=" * 70)
print("Environment Variables Check (Raw Values)")
print("=" * 70)

env_vars = {
    'DATABASE_URL': os.getenv("DATABASE_URL"),
    'DJANGO_SECRET_KEY': os.getenv("DJANGO_SECRET_KEY"),
    'DEBUG': os.getenv("DEBUG"),  # Note: settings.py uses 'DEBUG', not 'DJANGO_DEBUG'
    'RENDER_EXTERNAL_HOSTNAME': os.getenv("RENDER_EXTERNAL_HOSTNAME"),
    'DJANGO_ADMIN_INITIAL_PASSWORD': os.getenv("DJANGO_ADMIN_INITIAL_PASSWORD"),
}

print("\nVariables that settings.py READS:")
print("-" * 70)
for var, value in env_vars.items():
    if value:
        if 'SECRET' in var or 'PASSWORD' in var:
            display = f"<SET - {len(value)} characters>"
        else:
            display = value
        print(f"✅ {var}: {display}")
    else:
        print(f"❌ {var}: Not set (will use default/fallback)")

# Note about variables NOT read from env
print("\n" + "-" * 70)
print("Variables NOT read from environment (hardcoded):")
print("-" * 70)
print("❓ GA_MEASUREMENT_ID: Hardcoded in templates/base.html as 'G-9XJWT2P5LE'")
print("   (Not sensitive - acceptable to hardcode)")

# Now check what Django settings.py actually sees
print("\n" + "=" * 70)
print("Django Settings Values (What the app actually uses)")
print("=" * 70)

import django
django.setup()

from django.conf import settings

print("\nDEBUG:", settings.DEBUG)
print("  → From env var 'DEBUG' (defaults to False if not set)")

print("\nSECRET_KEY:", end=" ")
if settings.SECRET_KEY == 'django-insecure-dev-key-change-in-production-12345':
    print("<USING DEFAULT DEV KEY>")
    print("  ⚠️  Warning: Using insecure dev key - set DJANGO_SECRET_KEY in production!")
else:
    print(f"<SET - {len(settings.SECRET_KEY)} characters>")
    print("  ✅ Using value from DJANGO_SECRET_KEY environment variable")

print("\nDATABASE ENGINE:", settings.DATABASES['default']['ENGINE'])
if 'sqlite' in settings.DATABASES['default']['ENGINE']:
    print("  → Using SQLite (local development fallback)")
    print("  → DATABASE_URL not set, using default: sqlite:///db.sqlite3")
else:
    print("  → Using PostgreSQL (production)")
    print("  ✅ DATABASE_URL is set")

print("\nALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
if 'RENDER_EXTERNAL_HOSTNAME' in str(settings.ALLOWED_HOSTS):
    print("  → RENDER_EXTERNAL_HOSTNAME was added automatically")
else:
    print("  → Using hardcoded values (local dev + known Render URL)")

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print("\n✅ Variables correctly named and matching settings.py:")
print("   - DATABASE_URL")
print("   - DJANGO_SECRET_KEY")
print("   - DEBUG (not DJANGO_DEBUG)")
print("\n⚠️  Variables in your original script that don't match settings.py:")
print("   - DJANGO_DEBUG → Should be 'DEBUG'")
print("   - DJANGO_ALLOWED_HOSTS → Not used (ALLOWED_HOSTS configured differently)")
print("   - GA_MEASUREMENT_ID → Not read from env (hardcoded in template)")

print("\n" + "=" * 70)

