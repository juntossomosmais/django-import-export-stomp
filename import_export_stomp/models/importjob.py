import logging

from functools import partial

from author.decorators import with_author
from django.conf import settings
from django.db import models
from django.db import transaction
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from import_export.formats.base_formats import DEFAULT_FORMATS

from import_export_stomp.fields import ImportExportFileField
from import_export_stomp.utils import send_job_message_to_queue

logger = logging.getLogger(__name__)


@with_author
class ImportJob(models.Model):
    file = ImportExportFileField(
        verbose_name=_("File to be imported"),
        upload_to="django-import-export-stomp-import-jobs",
        blank=False,
        null=False,
        max_length=255,
    )

    processing_initiated = models.DateTimeField(
        verbose_name=_("Have we started processing the file? If so when?"),
        null=True,
        blank=True,
        default=None,
    )

    imported = models.DateTimeField(
        verbose_name=_("Has the import been completed? If so when?"),
        null=True,
        blank=True,
        default=None,
    )

    format = models.CharField(
        verbose_name=_("Format of file to be imported"),
        max_length=255,
    )

    change_summary = ImportExportFileField(
        verbose_name=_("Summary of changes made by this import"),
        upload_to="django-import-export-stomp-import-change-summaries",
        blank=True,
        null=True,
    )

    errors = models.TextField(
        verbose_name=_("Errors"),
        default="",
        blank=True,
    )

    model = models.CharField(
        verbose_name=_("Name of model to import to"),
        max_length=160,
    )

    job_status = models.CharField(
        verbose_name=_("Status of the job"),
        max_length=160,
        blank=True,
    )

    class Meta:
        verbose_name = _("Import job")
        verbose_name_plural = _("Import jobs")
        app_label = "import_export_stomp"

    @staticmethod
    def get_format_choices():
        """returns choices of available import formats"""
        return [
            (f.CONTENT_TYPE, f().get_title())
            for f in DEFAULT_FORMATS
            if f().can_import()
        ]


@receiver(post_save, sender=ImportJob)
def importjob_post_save(sender, instance, **kwargs):
    if not instance.processing_initiated:
        instance.processing_initiated = timezone.now()
        instance.save()
        transaction.on_commit(
            partial(
                send_job_message_to_queue,
                action="import",
                dry_run=getattr(settings, "IMPORT_DRY_RUN_FIRST_TIME", True),
                job_id=instance.pk,
            )
        )


@receiver(post_delete, sender=ImportJob)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file related to the import job
    """
    if instance.file:
        try:
            instance.file.delete()
        except Exception as e:
            logger.error("Some error occurred while deleting ImportJob file: %s", e)
        ImportJob.objects.filter(id=instance.id).delete()
