import uuid

from django.db import models
from falco_toolbox.models import TimeStamped

def file_object_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/filename
    return f"kitchenai/{uuid.uuid4()}/{filename}"

class KitchenAIManagement(TimeStamped):
    name = models.CharField(max_length=255, primary_key=True, default="kitchenai_management")
    project_name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    description = models.TextField(default="")

    def __str__(self):
        return self.name


class KitchenAIPlugins(TimeStamped):
    name = models.CharField(max_length=255, primary_key=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class KitchenAIDependencies(TimeStamped):
    name = models.CharField(max_length=255, primary_key=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class KitchenAIRootModule(TimeStamped):
    name = models.CharField(max_length=255, primary_key=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)

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

