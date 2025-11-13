from django.apps import AppConfig
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Startup hook that auto-creates admin user in production.
        
        Only runs when DEBUG=False and DJANGO_ADMIN_INITIAL_PASSWORD is set.
        Creates admin user if it doesn't exist, otherwise does nothing.
        """
        # Only run in production (DEBUG=False)
        if settings.DEBUG:
            return
        
        # Only proceed if password environment variable is set
        import os
        admin_password = os.environ.get('DJANGO_ADMIN_INITIAL_PASSWORD', '').strip()
        if not admin_password:
            return
        
        # Try to create admin user, but handle database errors gracefully
        # (in case migrations haven't run yet)
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Check if admin user already exists
            if User.objects.filter(username='admin').exists():
                return  # Admin already exists, do nothing
            
            # Create admin user
            User.objects.create_user(
                username='admin',
                email='chun-hung.yeh@yale.edu',
                password=admin_password,
                is_staff=True,
                is_superuser=True
            )
        except (OperationalError, ProgrammingError):
            # Database not ready yet (migrations not applied), just return
            return
        except Exception:
            # Any other error, fail silently in production
            return

