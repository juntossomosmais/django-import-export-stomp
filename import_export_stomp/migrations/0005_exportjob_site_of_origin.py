# Generated by Django 2.2.4 on 2019-11-13 13:27

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("import_export_stomp", "0004_exportjob_email_on_completion"),
    ]

    operations = [
        migrations.AddField(
            model_name="exportjob",
            name="site_of_origin",
            field=models.TextField(default="", max_length=255),
        ),
    ]
