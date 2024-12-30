# Generated by Django 5.1.2 on 2024-12-30 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bento", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoadedBento",
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
                ("settings", models.JSONField(default=dict)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
