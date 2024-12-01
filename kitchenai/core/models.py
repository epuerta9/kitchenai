import uuid

from django.db import models
from falco_toolbox.models import TimeStamped

def file_object_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/filename
    return f"kitchenai/{uuid.uuid4()}/{filename}"

def module_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/filename
    return f"kitchenai/modules/{filename}"

class KitchenAIManagement(TimeStamped):
    name = models.CharField(max_length=255, primary_key=True, default="kitchenai_management")
    project_name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    description = models.TextField(default="")
    jupyter_token = models.CharField(max_length=255, default="")
    jupyter_host = models.CharField(max_length=255, default="")
    jupyter_port = models.CharField(max_length=255, default="8888")
    jupyter_protocol = models.CharField(max_length=255, default="http")

    def __str__(self):
        return self.name


class KitchenAIPlugins(TimeStamped):
    name = models.CharField(max_length=255, unique=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class KitchenAIDependencies(TimeStamped):
    name = models.CharField(max_length=255, unique=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class KitchenAIRootModule(TimeStamped):
    name = models.CharField(max_length=255, unique=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)

class KitchenAIModule(TimeStamped):
    name = models.CharField(max_length=255)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)
    jupyter_path = models.CharField(max_length=255, default="")
    file = models.FileField(upload_to=module_directory_path)


class Notebook(TimeStamped):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

class CodeFunction(TimeStamped):
    class FuncType(models.TextChoices):
        STORAGE = "storage"
        EMBEDDING = "embedding"
        QUERY = "query"
        AGENT = "agent"

    hash = models.CharField(max_length=255)
    raw_code = models.TextField()
    code = models.TextField()
    type = models.CharField(max_length=255, choices=FuncType)
    label = models.CharField(max_length=255)
    notebook =  models.ForeignKey(Notebook, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return self.label

class CodeImport(TimeStamped):
    hash = models.CharField(max_length=255)
    code = models.TextField()
    notebook =  models.ForeignKey(Notebook, on_delete=models.CASCADE, blank=True, null=True)
    label =  models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"<notebook: {self.notebook}: {self.hash}>"
    
class CodeSetup(TimeStamped):
    hash = models.CharField(max_length=255)
    code = models.TextField()
    notebook =  models.ForeignKey(Notebook, on_delete=models.CASCADE, blank=True, null=True)
    label = models.CharField(max_length=255)


    def __str__(self) -> str:
        return f"<notebook: {self.notebook}: {self.hash}>"



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

