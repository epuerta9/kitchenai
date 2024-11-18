# Generated by Django 5.1.2 on 2024-11-18 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_delete_kitchenaimodules"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmbedObject",
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
                ("text", models.CharField(max_length=255)),
                ("ingest_label", models.CharField(max_length=255)),
                ("status", models.CharField(default="pending", max_length=255)),
                ("metadata", models.JSONField(default=dict)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]