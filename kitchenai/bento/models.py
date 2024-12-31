from django.db import models
from falco_toolbox.models import TimeStamped
from kitchenai.core.utils import add_package_to_core
from kitchenai.core.schema.rag import RAGConfigSchema
import logging

logger = logging.getLogger(__name__)    

class Bento(TimeStamped):
    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure only one instance exists for now. We'll do history of bento boxes later.
        if not self.pk and Bento.objects.exists():
            raise Exception("There can only be one Bento instance.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_import_path(self):
        return f"{self.name}.kitchen"
    
    def add_to_core(self):
        add_package_to_core(self.get_import_path())


class LoadedBento(TimeStamped):
    name = models.CharField(max_length=255)
    config = models.JSONField(default=dict)
    settings = models.JSONField(default=dict)

    class Meta:
        get_latest_by = 'updated_at'

    def __str__(self):
        return self.name

    @classmethod
    def get_current_config(cls, bento_name: str):
        """Get the latest configuration"""
        return cls.objects.get(name=bento_name)

    @classmethod
    def update_config(cls, bento_name: str, config: dict):
        """Create new configuration entry"""
        try:
            validated = RAGConfigSchema(**config)
            config_dict = validated.model_dump()
            return cls.objects.create(name=bento_name, config=config_dict)
        except Exception as e:
            logger.error(f"Error updating config for bento {bento_name}: {e}")
            return None

