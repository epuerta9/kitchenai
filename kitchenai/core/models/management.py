from django.db import models
from falco_toolbox.models import TimeStamped


class KitchenAIManagement(TimeStamped):
    name = models.CharField(
        max_length=255, primary_key=True, default="kitchenai_management"
    )
    version = models.CharField(max_length=255)
    description = models.TextField(default="")

    def __str__(self):
        return self.name




