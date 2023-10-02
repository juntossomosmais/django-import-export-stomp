import json
import logging

from uuid import UUID

from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from import_export_stomp.models import ExportJob
from import_export_stomp.utils import send_job_message_to_queue

logger = logging.getLogger(__name__)


def run_import_job_action(modeladmin, request, queryset):
    for instance in queryset:
        logger.info("Importing %s dry-run: False", instance.pk)
        send_job_message_to_queue(
            action="import",
            job_id=instance.pk,
            dry_run=False,
        )


run_import_job_action.short_description = _("Perform import")  # type: ignore


def run_import_job_action_dry(modeladmin, request, queryset):
    for instance in queryset:
        logger.info("Importing %s dry-run: True", instance.pk)
        send_job_message_to_queue(
            action="import",
            job_id=instance.pk,
            dry_run=True,
        )


run_import_job_action_dry.short_description = _("Perform dry import")  # type: ignore


def run_export_job_action(modeladmin, request, queryset):
    for instance in queryset:
        instance.processing_initiated = timezone.now()
        instance.save()
        send_job_message_to_queue(action="export", job_id=instance.pk)


run_export_job_action.short_description = _("Run export job")  # type: ignore


def create_export_job_action(modeladmin, request, queryset):
    if queryset:
        arbitrary_obj = queryset.first()
        ej = ExportJob.objects.create(
            app_label=arbitrary_obj._meta.app_label,
            model=arbitrary_obj._meta.model_name,
            queryset=json.dumps(
                [
                    str(obj.pk) if isinstance(obj.pk, UUID) else obj.pk
                    for obj in queryset
                ]
            ),
            site_of_origin=request.scheme + "://" + request.get_host(),
        )

    rurl = reverse(
        "admin:%s_%s_change"
        % (
            ej._meta.app_label,
            ej._meta.model_name,
        ),
        args=[ej.pk],
    )
    return redirect(rurl)


create_export_job_action.short_description = _("Export with stomp")  # type: ignore
