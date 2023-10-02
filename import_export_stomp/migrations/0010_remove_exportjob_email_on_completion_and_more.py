# Generated by Django 4.2.5 on 2023-10-02 02:33

from django.db import migrations
import import_export_stomp.fields
import storages.backends.s3


class Migration(migrations.Migration):
    dependencies = [
        (
            "import_export_stomp",
            "0009_alter_exportjob_options_alter_importjob_options_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="exportjob",
            name="email_on_completion",
        ),
        migrations.AlterField(
            model_name="exportjob",
            name="file",
            field=import_export_stomp.fields.ImportExportFileField(
                max_length=255,
                storage=storages.backends.s3.S3Storage(),
                upload_to="django-import-export-stomp-export-jobs",
                verbose_name="exported file",
            ),
        ),
        migrations.AlterField(
            model_name="importjob",
            name="change_summary",
            field=import_export_stomp.fields.ImportExportFileField(
                blank=True,
                null=True,
                storage=storages.backends.s3.S3Storage(),
                upload_to="django-import-export-stomp-import-change-summaries",
                verbose_name="Summary of changes made by this import",
            ),
        ),
        migrations.AlterField(
            model_name="importjob",
            name="file",
            field=import_export_stomp.fields.ImportExportFileField(
                max_length=255,
                storage=storages.backends.s3.S3Storage(),
                upload_to="django-import-export-stomp-import-jobs",
                verbose_name="File to be imported",
            ),
        ),
    ]
