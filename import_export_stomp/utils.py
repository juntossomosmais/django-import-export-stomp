from typing import Literal
from typing import Union
from uuid import uuid4

from django.conf import settings
from django_stomp.builder import build_publisher
from django_stomp.services.producer import auto_open_close_connection
from django_stomp.services.producer import do_inside_transaction
from import_export.formats.base_formats import DEFAULT_FORMATS

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
