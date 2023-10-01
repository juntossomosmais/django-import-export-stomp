import json

import pytest

from model_bakery import baker

from import_export_stomp.models import ExportJob
from import_export_stomp.pubsub import consumer
from tests.resources.fake_app.models import FakeModel
from tests.utils import create_payload


@pytest.mark.django_db
class TestExport:
    def test_should_export_model(self):
        ...
        # fake_models = baker.make(FakeModel, _quantity=3)

        # export_job = baker.make(
        #     ExportJob,
        #     format="text/csv",
        #     app_label="fake_app",
        #     model="fake_model",
        #     resource="FakeResource",
        #     queryset=json.dumps([str(fake_model.pk) for fake_model in fake_models]),
        # )

        # assert FakeModel.objects.count() == 0

        # payload, ack, nack = create_payload(
        #     {"action": "import", "dry_run": True, "job_id": str(export_job.pk)}
        # )

        # consumer(payload)

        # nack.assert_not_called()
        # ack.assert_called_once()

        # export_job.refresh_from_db()
        # assert "Import error" not in export_job.job_status

        # assert FakeModel.objects.count() == 0
