from typing import Literal
from typing import Type
from typing import Union
from uuid import uuid4

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.module_loading import import_string
from django_stomp.builder import build_publisher
from django_stomp.services.producer import auto_open_close_connection
from django_stomp.services.producer import do_inside_transaction
from import_export.formats.base_formats import DEFAULT_FORMATS

USE_GET_STORAGE_CLASS = DJANGO_VERSION < (4, 2)
if USE_GET_STORAGE_CLASS:
    from django.core.files.storage import get_storage_class as legacy_get_storage_class

IMPORT_EXPORT_STOMP_PROCESSING_QUEUE = getattr(
    settings,
    "IMPORT_EXPORT_STOMP_PROCESSING_QUEUE",
    "/queue/django-import-export-stomp-runner",
)


IMPORT_EXPORT_STOMP_EXCLUDED_FORMATS = getattr(
    settings,
    "IMPORT_EXPORT_STOMP_EXCLUDED_FORMATS",
    [],
)


def get_storage_class(import_path: str | None = None) -> Type[Storage]:
    if USE_GET_STORAGE_CLASS:
        return legacy_get_storage_class(import_path)
    else:
        return import_string(import_path or settings.DEFAULT_FILE_STORAGE)


def get_formats():
    return [
        format
        for format in DEFAULT_FORMATS
        if format.TABLIB_MODULE.split(".")[-1].strip("_")
        not in IMPORT_EXPORT_STOMP_EXCLUDED_FORMATS
    ]


def send_job_message_to_queue(
    action: Union[Literal["import"], Literal["export"]],
    job_id: int,
    dry_run: bool = False,
) -> None:
    publisher = build_publisher(f"django-import-export-stomp-{str(uuid4())}")

    with auto_open_close_connection(publisher), do_inside_transaction(publisher):
        publisher.send(
            queue=IMPORT_EXPORT_STOMP_PROCESSING_QUEUE,
            body={"action": action, "job_id": str(job_id), "dry_run": dry_run},
        )
