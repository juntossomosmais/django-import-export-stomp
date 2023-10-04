import csv
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
        fake_models = baker.make(FakeModel, _quantity=3)

        export_job = baker.make(
            ExportJob,
            format="text/csv",
            app_label="fake_app",
            model="fakemodel",
            resource="FakeResource",
            queryset=json.dumps([str(fake_model.pk) for fake_model in fake_models]),
        )

        assert FakeModel.objects.count() == 3

        payload, ack, nack = create_payload(
            {"action": "export", "dry_run": False, "job_id": str(export_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        export_job.refresh_from_db()
        export_job.job_status = "Export complete"

        with export_job.file.open("r") as file:
            csv_data = list(csv.DictReader(file))

            for index, dict_row in enumerate(csv_data):
                dict_row["name"] = fake_models[index].name
                dict_row["value"] = fake_models[index].value
