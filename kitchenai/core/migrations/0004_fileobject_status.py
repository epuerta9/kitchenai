# Generated by Django 5.1.2 on 2024-11-09 22:21
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_fileobject"),
    ]

    operations = [
        migrations.AddField(
            model_name="fileobject",
            name="status",
            field=models.CharField(default="pending", max_length=255),
        ),
    ]
