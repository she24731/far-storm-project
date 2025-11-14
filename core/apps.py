from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Startup hook that ensures admin user exists and is up-to-date.
        
        Requires DJANGO_ADMIN_INITIAL_PASSWORD environment variable to be set.
        Creates admin user if it doesn't exist, or updates password and flags if it does.
        """
        import os
        
        # Only proceed if password environment variable is set
        admin_password = os.environ.get('DJANGO_ADMIN_INITIAL_PASSWORD', '').strip()
        if not admin_password:
            return
        
        # Try to create or update admin user, but handle database errors gracefully
        # (in case migrations haven't run yet)
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get or create admin user
            user, created = User.objects.get_or_create(
                username='admin',
                defaults={'email': 'chun-hung.yeh@yale.edu'},
            )
            
            # Always ensure admin user has correct flags and password
            user.is_staff = True
            user.is_superuser = True
            user.set_password(admin_password)
            user.save()
        except (OperationalError, ProgrammingError):
            # Database not ready yet (migrations not applied), just return
            return
        except Exception:
            # Any other error, fail silently
            return

