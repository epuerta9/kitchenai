from django.db import models
from falco_toolbox.models import TimeStamped
from django.conf import settings

def module_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/filename
    return f"kitchenai/modules/{filename}"


class KitchenAIManagement(TimeStamped):
    name = models.CharField(
        max_length=255, primary_key=True, default="kitchenai_management"
    )
    version = models.CharField(max_length=255)
    description = models.TextField(default="")

    def __str__(self):
        return self.name


class KitchenAIPlugins(TimeStamped):
    name = models.CharField(max_length=255, unique=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)

    def __str__(self):
        return self.name




