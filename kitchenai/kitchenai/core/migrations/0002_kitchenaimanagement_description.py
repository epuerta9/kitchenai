# Generated by Django 5.1.2 on 2024-10-19 16:51
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="kitchenaimanagement",
            name="description",
            field=models.TextField(default=""),
        ),
    ]
