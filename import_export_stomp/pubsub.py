import logging

from typing import Union
from uuid import UUID

from django_stomp.services.consumer import Payload

from import_export_stomp.models import ExportJob
from import_export_stomp.models import ImportJob

logger = logging.getLogger(__name__)

ACTIONS = ("import", "export")


def validate_payload(payload: Payload):
    assert "action" in payload.body, "Payload needs to have 'action' key set."
    assert (
        payload.body["action"] in ACTIONS
    ), "Action value needs to be 'import' or 'export'."
    assert "job_id" in payload.body, "Payload needs to have 'job_id' key set."

    try:
        UUID(payload.body["job_id"])
    except ValueError:
        raise AssertionError("'job_id' is not a valid UUID.") from ValueError


def get_job_object(payload: Payload) -> Union[ImportJob, ExportJob]:
    filters = {
        "pk": payload.body["job_id"],
    }
    return (
        ImportJob.objects.get(**filters | {"imported__isnull": True})
        if payload.body["action"] == "import"
        else ExportJob.objects.get(**filters)
    )


def consumer(payload: Payload):
    """
    {
        "action": "import",
        "job_id": "9734b8b2-598d-4925-87da-20d453cab9d8"
    }
    """

    try:
        validate_payload(payload)
    except AssertionError as exc:
        logger.warning(str(exc))
        # Since the error is unrecoverable we will only ack
        return payload.ack()

    # Run action and ack
