from typing import Callable
from unittest.mock import ANY, MagicMock
from unittest.mock import Mock

import pytest

from model_bakery import baker
from pytest_mock import MockerFixture
from django.forms import model_to_dict

import import_export_stomp.utils

from import_export_stomp.admin import ImportJobAdmin
import import_export_stomp.admin_actions
from import_export_stomp.admin_actions import run_export_job_action
from import_export_stomp.admin_actions import run_import_job_action
from import_export_stomp.admin_actions import (
    run_import_job_action_dry,
    create_export_job_action,
)
from import_export_stomp.models import ExportJob
from import_export_stomp.models import ImportJob
from import_export_stomp.utils import IMPORT_EXPORT_STOMP_PROCESSING_QUEUE
from tests.resources.fake_app.models import FakeModel


@pytest.mark.django_db
class TestActions:
    @pytest.mark.parametrize(
        ("fn", "expected_dry_run"),
        ((run_import_job_action, False), (run_import_job_action_dry, True)),
    )
    def test_run_import_job_action(
        self, mocker: MockerFixture, fn: Callable, expected_dry_run: bool
    ):
        import_job = baker.make(ImportJob)
        mocked_send = mocker.MagicMock()
        mocker.patch.object(
            import_export_stomp.utils, "build_publisher", return_value=mocked_send
        )

        fn(MagicMock(), MagicMock(), ImportJob.objects.all())

        mocked_send.send.assert_called_with(
            queue=IMPORT_EXPORT_STOMP_PROCESSING_QUEUE,
            body={
                "action": "import",
                "job_id": str(import_job.pk),
                "dry_run": expected_dry_run,
            },
        )

    def test_run_export_job_action(self, mocker: MockerFixture):
        export_job = baker.make(ExportJob)
        mocked_send = mocker.MagicMock()
        mocker.patch.object(
            import_export_stomp.utils, "build_publisher", return_value=mocked_send
        )

        run_export_job_action(MagicMock(), MagicMock(), ExportJob.objects.all())

        mocked_send.send.assert_called_with(
            queue=IMPORT_EXPORT_STOMP_PROCESSING_QUEUE,
            body={"action": "export", "job_id": str(export_job.pk), "dry_run": False},
        )

    def test_run_create_export_job_action(self, mocker: MockerFixture):
        mocked_reverse = mocker.patch.object(
            import_export_stomp.admin_actions, "reverse"
        )
        mocked_reverse.return_value = "fake"

        mocked_redirect = mocker.patch.object(
            import_export_stomp.admin_actions, "redirect"
        )
        mocked_redirect.return_value = "fake"

        modeladmin_mock = MagicMock()
        request_mock = MagicMock()
        request_mock.scheme = "https://"
        request_mock.get_host = MagicMock(return_value="fake")

        assert ExportJob.objects.count() == 0

        fake_entry = baker.make(FakeModel)

        create_export_job_action(
            modeladmin=modeladmin_mock,
            request=request_mock,
            queryset=FakeModel.objects.all(),
        )

        assert ExportJob.objects.count() == 1
        export_job = ExportJob.objects.get()

        assert model_to_dict(export_job) == {
            "id": 1,
            "file": ANY,
            "processing_initiated": None,
            "job_status": "",
            "format": None,
            "app_label": "fake_app",
            "model": "fakemodel",
            "resource": "",
            "queryset": f"[{fake_entry.pk}]",
            "site_of_origin": ANY,
            "author": None,
            "updated_by": None,
        }
