from django.apps import AppConfig
from django.contrib import admin


class SiteConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.site_config"

    def ready(self):
        """
        This method is called when the app is ready.
        We monkey-patch the default admin site's index view here.
        """
        # Import the data gathering function here to avoid startup issues
        from .utils import get_dashboard_context

        # Get a reference to the default admin site
        admin_site = admin.site

        # Store the original index view so we can call it later
        original_index = admin_site.index

        def new_index(request, extra_context=None):
            """
            Our new custom index view that injects dashboard data.
            """
            extra_context = extra_context or {}
            extra_context.update(get_dashboard_context())

            # Call the original index view with our new, richer context
            return original_index(request, extra_context)

        # Replace the default admin's index method with our new one
        admin_site.index = new_index
