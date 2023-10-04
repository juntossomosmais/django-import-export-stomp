import pytest

from django.core.files.base import ContentFile
from model_bakery import baker

from import_export_stomp.models import ImportJob
from import_export_stomp.pubsub import consumer
from tests.resources.fake_app.models import FakeModel
from tests.utils import create_payload


@pytest.mark.django_db
class TestImport:
    @pytest.fixture
    def csv_file(self) -> ContentFile:
        return ContentFile(
            b"name,value\nname1,1\nname2,2",
            name="import_csv.csv",
        )

    def test_should_import_to_model_dry_run(self, csv_file: ContentFile):
        import_job = baker.make(
            ImportJob, file=csv_file, model="Test", format="text/csv"
        )

        assert FakeModel.objects.count() == 0

        payload, ack, nack = create_payload(
            {"action": "import", "dry_run": True, "job_id": str(import_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        import_job.refresh_from_db()
        assert import_job.job_status == "[Dry run] 5/5 Import job finished"
        assert import_job.imported is None

        assert FakeModel.objects.count() == 0

    def test_should_import_to_model(self, csv_file: ContentFile):
        import_job = baker.make(
            ImportJob, file=csv_file, model="Test", format="text/csv"
        )

        assert FakeModel.objects.count() == 0

        payload, ack, nack = create_payload(
            {"action": "import", "dry_run": False, "job_id": str(import_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        import_job.refresh_from_db()
        assert "Import error" not in import_job.job_status

        assert FakeModel.objects.count() == 2
        row_1, row_2 = FakeModel.objects.order_by("id").all()

        assert row_1.name == "name1"
        assert row_1.value == 1
        assert row_2.name == "name2"
        assert row_2.value == 2
