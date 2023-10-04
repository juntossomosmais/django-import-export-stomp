import logging

from typing import Callable
from typing import Tuple
from typing import Union

from django_stomp.services.consumer import Payload

from import_export_stomp.models import ExportJob
from import_export_stomp.models import ImportJob
from import_export_stomp.tasks import run_export_job
from import_export_stomp.tasks import run_import_job

logger = logging.getLogger(__name__)

ACTIONS = ("import", "export")


def validate_payload(payload: Payload):
    assert "action" in payload.body, "Payload needs to have 'action' key set."
    assert (
        payload.body["action"] in ACTIONS
    ), "Action value needs to be 'import' or 'export'."
    assert "dry_run" in payload.body, "Payload needs to have 'dry_run' key set."
    assert isinstance(payload.body["dry_run"], bool), "'dry_run' is not a boolean."
    assert "job_id" in payload.body, "Payload needs to have 'job_id' key set."
    assert payload.body["job_id"].isnumeric(), "'job_id' is not a number."


def get_job_object_and_runner(
    payload: Payload,
) -> Union[Tuple[ImportJob, Callable], Tuple[ExportJob, Callable]]:
    filters = {
        "pk": payload.body["job_id"],
    }
    return (
        (ImportJob.objects.get(**filters | {"imported__isnull": True}), run_import_job)
        if payload.body["action"] == "import"
        else (ExportJob.objects.get(**filters), run_export_job)
    )


def consumer(payload: Payload):
    """
    Consumer that processes both import/export jobs.

    Expected payload example:
    {
        "action": "import",
        "dry_run": True,
        "job_id": "9734b8b2-598d-4925-87da-20d453cab9d8"
    }
    """

    try:
        validate_payload(payload)
    except AssertionError as exc:
        logger.warning(str(exc))
        # Since the error is unrecoverable we will only ack
        return payload.ack()

    job, runner = get_job_object_and_runner(payload)
    runner(job, dry_run=payload.body["dry_run"])

    return payload.ack()
