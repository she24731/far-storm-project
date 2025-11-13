"""
WSGI config for yale_newcomer_survival_guide project.

WSGI (Web Server Gateway Interface) is the standard interface between
web servers and Python web applications. This file exposes the WSGI
callable as a module-level variable named 'application'.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yale_newcomer_survival_guide.settings')

application = get_wsgi_application()

