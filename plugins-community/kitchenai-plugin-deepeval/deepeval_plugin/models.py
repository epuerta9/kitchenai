from django.db import models
from falco_toolbox.models import TimeStamped


# Create your models here.
class DataSet(TimeStamped):
    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Evaluation {self.name}"
    

class Settings(TimeStamped):
    name = models.CharField(max_length=255)
    is_answer_relevance_enabled = models.BooleanField(default=True)
    is_faithfulness_enabled = models.BooleanField(default=True)
    is_contextual_relevancy_enabled = models.BooleanField(default=True)
    is_hallucination_enabled = models.BooleanField(default=True)
    is_toxicity_enabled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            # If trying to create a new object when one already exists, return existing
            return Settings.objects.first()
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(defaults={'name': 'Default Settings'})
        return obj
    @classmethod    
    async def aget_settings(cls):
        obj, created = await cls.objects.aget_or_create(defaults={'name': 'Default Settings'})
        return obj


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

class Faithfulness(TimeStamped):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    statements = models.JSONField(default=list)
    verdicts = models.JSONField(default=list)
    score = models.FloatField(default=0.0)
    reason = models.TextField(default="")
    success = models.BooleanField(default=False)
    verbose_logs = models.JSONField(default=list)

    def __str__(self):
        return f"Faithfulness {self.data.id}"

class ContextualRelevancy(TimeStamped):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    statements = models.JSONField(null=True)
    verdicts = models.JSONField(null=True)
    score = models.FloatField()
    reason = models.TextField(null=True)
    success = models.BooleanField()
    verbose_logs = models.JSONField(null=True)

    class Meta:
        verbose_name_plural = "Contextual Relevancy"

class Hallucination(TimeStamped):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    statements = models.JSONField(null=True)
    verdicts = models.JSONField(null=True)
    score = models.FloatField()
    reason = models.TextField(null=True)
    success = models.BooleanField()
    verbose_logs = models.JSONField(null=True)

    class Meta:
        verbose_name_plural = "Hallucinations"

class Toxicity(TimeStamped):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    statements = models.JSONField(null=True)
    verdicts = models.JSONField(null=True)
    score = models.FloatField()
    reason = models.TextField(null=True)
    success = models.BooleanField()
    verbose_logs = models.JSONField(null=True)

    class Meta:
        verbose_name_plural = "Toxicity"

    def __str__(self):
        return f"Toxicity {self.data.id}"
