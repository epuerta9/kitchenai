# Generated by Django 5.1.2 on 2025-01-18 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bento", "0002_remoteclient_last_seen"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="remoteclient",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="remoteclient",
            name="version",
            field=models.CharField(default="0.0.1", max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name="remoteclient",
            unique_together={("name", "client_id", "version")},
        ),
    ]
