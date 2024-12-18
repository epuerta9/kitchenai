from django.db import models
from falco_toolbox.models import TimeStamped


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
