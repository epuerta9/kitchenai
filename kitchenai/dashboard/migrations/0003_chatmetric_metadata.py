# Generated by Django 5.1.2 on 2024-12-31 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_chatsetting_metadata"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmetric",
            name="metadata",
            field=models.JSONField(default=dict),
        ),
    ]
