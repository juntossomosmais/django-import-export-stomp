from uuid import UUID

from django_stomp.services.consumer import Payload

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


def get_job_object(payload: Payload):
    ...


def consumer(payload: Payload):
    """
    {
        "action": "import",
        "job_id": "9734b8b2-598d-4925-87da-20d453cab9d8"
    }
    """

    # Validate payload

    # Select which action to run

    # Run action and ack
