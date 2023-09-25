from contextlib import nullcontext
from functools import partial
from typing import Callable
from typing import Dict

import pytest

from import_export_stomp.pubsub import validate_payload
from tests.utils import create_payload


class TestValidatePayload:
    @pytest.mark.parametrize(
        ("data", "context"),
        (
            (
                {},
                partial(
                    pytest.raises,
                    AssertionError,
                    match="Payload needs to have 'action' key set.",
                ),
            ),
            (
                {"abc": True},
                partial(
                    pytest.raises,
                    AssertionError,
                    match="Payload needs to have 'action' key set.",
                ),
            ),
            (
                {"action": "invalid", "job_id": "invalid"},
                partial(
                    pytest.raises,
                    AssertionError,
                    match="Action value needs to be 'import' or 'export'.",
                ),
            ),
            (
                {"action": "import"},
                partial(
                    pytest.raises,
                    AssertionError,
                    match="Payload needs to have 'job_id' key set.",
                ),
            ),
            (
                {"action": "import", "job_id": "invalid"},
                partial(
                    pytest.raises, AssertionError, match="'job_id' is not a valid UUID."
                ),
            ),
            (
                {"action": "export", "job_id": "invalid"},
                partial(
                    pytest.raises, AssertionError, match="'job_id' is not a valid UUID."
                ),
            ),
            (
                {"action": "import", "job_id": "03d52eda-1394-4bf1-aca2-a61d8b8be429"},
                nullcontext,
            ),
            (
                {"action": "export", "job_id": "03d52eda-1394-4bf1-aca2-a61d8b8be429"},
                nullcontext,
            ),
        ),
    )
    def test_payload_should_be_validated(self, data: Dict, context: Callable):
        payload, _, _ = create_payload(data)
        with context():
            validate_payload(payload)
