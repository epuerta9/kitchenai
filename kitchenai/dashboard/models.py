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
    input_text = models.TextField(default="n/a")
    output_text = models.TextField(default="n/a")
    sources_used = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    embedding_tokens = models.IntegerField(default=0)
    llm_prompt_tokens = models.IntegerField(default=0) 
    llm_completion_tokens = models.IntegerField(default=0)
    total_llm_tokens = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.chat.name} - {self.created_at}"


class AggregatedChatMetric(TimeStamped):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    embedding_tokens = models.IntegerField(default=0)
    llm_prompt_tokens = models.IntegerField(default=0) 
    llm_completion_tokens = models.IntegerField(default=0)
    total_llm_tokens = models.IntegerField(default=0)
    total_interactions = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.chat.name} - {self.chat.created_at} - Total Tokens: {self.total_llm_tokens}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['chat_id'], name='unique_chat_metrics')
        ]


