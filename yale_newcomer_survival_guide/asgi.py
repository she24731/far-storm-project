"""
ASGI config for yale_newcomer_survival_guide project.

ASGI (Asynchronous Server Gateway Interface) is a standard interface
for async Python web servers and applications.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yale_newcomer_survival_guide.settings')

application = get_asgi_application()

