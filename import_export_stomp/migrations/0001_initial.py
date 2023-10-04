# Generated by Django 2.0.12 on 2019-06-28 13:55

import django.db.models.deletion

from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to="django-import-export-stomp-import-jobs",
                        verbose_name="File to be imported",
                    ),
                ),
                (
                    "processing_initiated",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Have we started processing the file? If so when?",
                    ),
                ),
                (
                    "imported",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Has the import been completed? If so when?",
                    ),
                ),
                (
                    "format",
                    models.CharField(
                        choices=[
                            ("text/csv", "text/csv"),
                            ("application/vnd.ms-excel", "application/vnd.ms-excel"),
                            (
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            ),
                            ("text/tab-separated-values", "text/tab-separated-values"),
                            (
                                "application/vnd.oasis.opendocument.spreadsheet",
                                "application/vnd.oasis.opendocument.spreadsheet",
                            ),
                            ("application/json", "application/json"),
                            ("text/yaml", "text/yaml"),
                            ("text/html", "text/html"),
                        ],
                        max_length=40,
                        verbose_name="Format of file to be imported",
                    ),
                ),
                (
                    "change_summary",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="django-import-export-stomp-import-change-summaries",
                        verbose_name="Summary of changes made by this import",
                    ),
                ),
                ("errors", models.TextField(blank=True, default="")),
                (
                    "model",
                    models.CharField(
                        choices=[("Winner", "Winner")],
                        max_length=160,
                        verbose_name="Name of model to import to",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="importjob_create",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="author",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="importjob_update",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="last updated by",
                    ),
                ),
            ],
        ),
    ]
