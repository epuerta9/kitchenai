from django.db import models
from falco_toolbox.models import TimeStamped


class Plugin(TimeStamped):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
