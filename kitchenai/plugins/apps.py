from django.apps import AppConfig
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_migrate



class PluginsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai.plugins"

    def ready(self):
        """Check the list of loaded plugins and check for them in the database"""
        from .models import Plugin
        from django.conf import settings

        
        def sync_plugins(sender, **kwargs):
            """Synchronize plugins with the database after migrations."""
            loaded_plugins = settings.KITCHENAI.get('plugins', [])
            
            # First delete plugins that are no longer loaded
            Plugin.objects.exclude(name__in=loaded_plugins).delete()

            # Then create any new plugins that are loaded but not in DB
            for plugin_name in loaded_plugins:
                try:
                    # Check if the plugin exists in the database
                    Plugin.objects.get(name=plugin_name)
                except ObjectDoesNotExist:
                    # Handle the case where the plugin is not found
                    Plugin.objects.create(name=plugin_name)

        post_migrate.connect(sync_plugins, sender=self)