from django.db import models
from falco_toolbox.models import TimeStamped


class KitchenAIManagement(TimeStamped):
    name = models.CharField(max_length=255, primary_key=True, default="kitchenai_management")


    def __str__(self):
        return self.name


class KitchenAIModules(TimeStamped):
    name = models.CharField(max_length=255, primary_key=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)


    def __str__(self):
        return self.name
