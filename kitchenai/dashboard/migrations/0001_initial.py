# Generated by Django 5.1.2 on 2025-01-17 04:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Chat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("alias", models.CharField(default="", max_length=255)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Dashboard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ChatMetric",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("input_text", models.TextField(default="n/a")),
                ("output_text", models.TextField(default="n/a")),
                ("sources_used", models.JSONField(default=list)),
                ("metadata", models.JSONField(default=dict)),
                ("embedding_tokens", models.IntegerField(default=0)),
                ("llm_prompt_tokens", models.IntegerField(default=0)),
                ("llm_completion_tokens", models.IntegerField(default=0)),
                ("total_llm_tokens", models.IntegerField(default=0)),
                (
                    "chat",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="dashboard.chat"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ChatSetting",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "chat_type",
                    models.CharField(
                        choices=[("query", "Query"), ("agent", "Agent")],
                        default="query",
                        max_length=255,
                    ),
                ),
                ("selected_label", models.CharField(default="", max_length=255)),
                ("bento_name", models.CharField(default="", max_length=255)),
                ("metadata", models.JSONField(default=dict)),
                (
                    "chat",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="dashboard.chat"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AggregatedChatMetric",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("embedding_tokens", models.IntegerField(default=0)),
                ("llm_prompt_tokens", models.IntegerField(default=0)),
                ("llm_completion_tokens", models.IntegerField(default=0)),
                ("total_llm_tokens", models.IntegerField(default=0)),
                ("total_interactions", models.IntegerField(default=0)),
                (
                    "chat",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="dashboard.chat"
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("chat_id",), name="unique_chat_metrics"
                    )
                ],
            },
        ),
    ]
