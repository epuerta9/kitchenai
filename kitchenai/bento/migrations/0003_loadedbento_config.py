# Generated by Django 5.1.2 on 2024-12-30 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bento", "0002_loadedbento"),
    ]

    operations = [
        migrations.AddField(
            model_name="loadedbento",
            name="config",
            field=models.JSONField(default=dict),
        ),
    ]
