# Generated by Django 5.1.2 on 2025-01-02 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("deepeval_plugin", "0003_remove_answerrelevance_relevance_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="data",
            name="source_id",
            field=models.IntegerField(default=0),
        ),
    ]
