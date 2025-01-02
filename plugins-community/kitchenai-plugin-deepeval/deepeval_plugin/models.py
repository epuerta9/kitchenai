from django.db import models
from falco_toolbox.models import TimeStamped


# Create your models here.
class DataSet(TimeStamped):
    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Evaluation {self.name}"


class Data(TimeStamped):
    source_id = models.IntegerField(default=0)
    input = models.TextField()
    output = models.TextField()
    retrieval_context = models.JSONField(default=list)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)


class AnswerRelevance(TimeStamped):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    statements = models.JSONField(default=list)
    verdicts = models.JSONField(default=list)
    score = models.FloatField(default=0.0)
    reason = models.TextField(default="")
    success = models.BooleanField(default=False)
    verbose_logs = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"Answer Relevance {self.data.id}"
