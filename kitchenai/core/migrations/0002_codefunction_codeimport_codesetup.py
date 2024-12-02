# Generated by Django 5.1.2 on 2024-11-29 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CodeFunction",
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
                ("hash", models.CharField(max_length=255)),
                ("raw_code", models.TextField()),
                ("code", models.TextField()),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("storage", "Storage"),
                            ("embedding", "Embedding"),
                            ("query", "Query"),
                            ("agent", "Agent"),
                        ],
                        max_length=255,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CodeImport",
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
                ("hash", models.CharField(max_length=255)),
                ("code", models.TextField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CodeSetup",
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
                ("hash", models.CharField(max_length=255)),
                ("code", models.TextField()),
            ],
            options={
                "abstract": False,
            },
        ),
    ]