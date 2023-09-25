from contextlib import nullcontext
from functools import partial
from typing import Callable
from typing import Dict

import pytest

from model_bakery import baker

from import_export_stomp.models import ExportJob
from import_export_stomp.models import ImportJob
from import_export_stomp.pubsub import get_job_object_and_runner
from import_export_stomp.pubsub import validate_payload
from import_export_stomp.tasks import run_export_job
from import_export_stomp.tasks import run_import_job
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


@pytest.mark.django_db
class TestGetJobObject:
    def test_should_correct_fetch_import_job(self):
        import_job = baker.make(ImportJob)
        payload, _, _ = create_payload(
            {"action": "import", "job_id": str(import_job.pk)}
        )

        job, runner = get_job_object_and_runner(payload)

        assert job.pk == import_job.pk
        assert runner == run_import_job

    def test_should_correct_fetch_export_job(self):
        export_job = baker.make(ExportJob)
        payload, _, _ = create_payload(
            {"action": "export", "job_id": str(export_job.pk)}
        )

        job, runner = get_job_object_and_runner(payload)

        assert job.pk == export_job.pk
        assert runner == run_export_job

    def test_should_raise_does_not_exists_when_import_job_does_not_exists(self):
        payload, _, _ = create_payload({"action": "import", "job_id": "9999"})
        with pytest.raises(ImportJob.DoesNotExist):
            get_job_object_and_runner(payload)

    def test_should_raise_does_not_exists_when_export_job_does_not_exists(self):
        payload, _, _ = create_payload({"action": "export", "job_id": "9999"})
        with pytest.raises(ExportJob.DoesNotExist):
            get_job_object_and_runner(payload)
