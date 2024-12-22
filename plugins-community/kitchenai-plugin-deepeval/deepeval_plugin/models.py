from django.db import models
from falco_toolbox.models import TimeStamped


# Create your models here.
class DataSet(TimeStamped):
    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Evaluation {self.name}"


class Data(TimeStamped):
    input = models.TextField()
    output = models.TextField()
    retrieval_context = models.JSONField(default=list)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)



