# Generated by Django 4.0.6 on 2023-05-15 16:34

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("import_export_stomp", "0007_auto_20210210_1831"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exportjob",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="importjob",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
