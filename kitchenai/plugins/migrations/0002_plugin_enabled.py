# Generated by Django 5.1.2 on 2024-12-22 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plugins", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="plugin",
            name="enabled",
            field=models.BooleanField(default=False),
        ),
    ]
