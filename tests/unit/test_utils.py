import contextlib

from sys import modules

import import_export
import pytest

from pytest_mock import MockerFixture
from tests.utils import create_payload

import import_export_stomp.utils

from import_export_stomp.utils import IMPORT_EXPORT_STOMP_PROCESSING_QUEUE
from import_export_stomp.utils import get_formats
from import_export_stomp.utils import resource_importer
from import_export_stomp.utils import send_job_message_to_queue


@pytest.mark.django_db
class TestUtils:
    def test_get_formats(self):
        CSV = import_export.formats.base_formats.CSV
        XLSX = import_export.formats.base_formats.XLSX
        with contextlib.suppress(ImportError):
            formats = get_formats()
            assert CSV in formats
            assert XLSX in formats


class TestSendMessageToQueue:
    @pytest.mark.parametrize("action", ("import", "export"))
    def test_should_send_message_to_defult_queue(
        self, action: str, mocker: MockerFixture
    ):
        mocked_send = mocker.MagicMock()
        mocker.patch.object(
            import_export_stomp.utils, "build_publisher", return_value=mocked_send
        )
        job_id = 9999
        send_job_message_to_queue(action, job_id)

        mocked_send.send.assert_called_with(
            queue=IMPORT_EXPORT_STOMP_PROCESSING_QUEUE,
            body={"action": action, "job_id": str(job_id)},
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
