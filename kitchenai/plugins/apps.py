from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class PluginsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai.plugins"

    def ready(self):
        """Check the list of loaded plugins and check for them in the database"""
        from .models import Plugin
        loaded_plugins = settings.KITCHENAI.get('plugins', [])
        
        for plugin_name in loaded_plugins:
            try:
                # Check if the plugin exists in the database
                Plugin.objects.get(name=plugin_name)
            except ObjectDoesNotExist:
                # Handle the case where the plugin is not found
                Plugin.objects.create(name=plugin_name)
        
