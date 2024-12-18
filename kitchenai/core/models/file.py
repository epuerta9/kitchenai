
import uuid

from django.db import models
from falco_toolbox.models import TimeStamped

def file_object_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/filename
    return f"kitchenai/{uuid.uuid4()}/{filename}"

class FileObject(TimeStamped):
    """
    This is a model for any file that is uploaded to the system.
    It will be used to trigger any storage tasks or other processes
    """
    class Status(models.TextChoices):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    file = models.FileField(upload_to=file_object_directory_path)
    name = models.CharField(max_length=255)
    ingest_label = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default=Status.PENDING)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.name