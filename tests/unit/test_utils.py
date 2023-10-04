import contextlib

from sys import modules

import import_export
import pytest

from pytest_mock import MockerFixture

import import_export_stomp.utils

from import_export_stomp.utils import IMPORT_EXPORT_STOMP_PROCESSING_QUEUE
from import_export_stomp.utils import get_formats
from import_export_stomp.utils import resource_importer
from import_export_stomp.utils import send_job_message_to_queue
from tests.utils import create_payload


@pytest.mark.django_db
class TestUtils:
    def test_get_formats(self) -> None:
        CSV = import_export.formats.base_formats.CSV
        XLSX = import_export.formats.base_formats.XLSX
        with contextlib.suppress(ImportError):
            formats = get_formats()
            assert CSV in formats
            assert XLSX in formats


class TestSendMessageToQueue:
    @pytest.mark.parametrize(
        ("action", "dry_run"),
        (("import", False), ("import", True), ("export", False), ("export", True)),
    )
    def test_should_send_message_to_defult_queue(
        self, action: str, dry_run: bool, mocker: MockerFixture
    ):
        mocked_send = mocker.MagicMock()
        mocker.patch.object(
            import_export_stomp.utils, "build_publisher", return_value=mocked_send
        )
        job_id = 9999
        send_job_message_to_queue(action, job_id, dry_run)

        mocked_send.send.assert_called_with(
            queue=IMPORT_EXPORT_STOMP_PROCESSING_QUEUE,
            body={"action": action, "job_id": str(job_id), "dry_run": dry_run},
        )


class TestResourceImporter:
    def test_should_import_module_from_string(self):
        imported = resource_importer("tests.utils.create_payload")

        assert "tests.utils" in modules.keys()
        assert imported() == create_payload

    def test_should_fail_to_import_inexisting_module(self):
        imported = resource_importer("fake.module.fake_function")

        with pytest.raises(ModuleNotFoundError):
            imported()
