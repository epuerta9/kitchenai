from django.db import models
from falco_toolbox.models import TimeStamped


class EmbedObject(TimeStamped):
    """
    This is a model for any embed object that is created
    """
    class Status(models.TextChoices):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    text = models.CharField(max_length=255)
    ingest_label = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default=Status.PENDING)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.text
