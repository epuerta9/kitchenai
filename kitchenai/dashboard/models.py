from django.db import models
from falco_toolbox.models import TimeStamped
from django_q.tasks import async_task

class Dashboard(TimeStamped):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Chat(TimeStamped):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, default="")

class ChatSetting(TimeStamped):
    class ChatType(models.TextChoices):
        QUERY = "query", "Query"
        AGENT = "agent", "Agent"

    chat = models.OneToOneField(Chat, on_delete=models.CASCADE)
    chat_type = models.CharField(max_length=255, choices=ChatType.choices, default=ChatType.QUERY)
    selected_label = models.CharField(max_length=255, default="")
    bento_name = models.CharField(max_length=255, default="")
    metadata = models.JSONField(default=dict)

class ChatMetric(TimeStamped):
    input_text = models.TextField(default="")
    output_text = models.TextField(default="")
    response_time = models.FloatField(default=0)
    token_usage = models.IntegerField(default=0)
    confidence_score = models.IntegerField(default=0)
    sources_used = models.JSONField(default=list)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.chat.name} - {self.response_time}s"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        async_task("kitchenai.dashboard.tasks.update_aggregated_metrics", self)


class AggregatedChatMetric(TimeStamped):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    avg_response_time = models.FloatField(default=0)
    total_token_usage = models.IntegerField(default=0) 
    avg_confidence_score = models.FloatField(default=0)
    total_interactions = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.chat.name} - {self.chat.created_at} - Total Tokens: {self.total_token_usage} "

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['chat_id'], name='unique_chat_metrics')
        ]
