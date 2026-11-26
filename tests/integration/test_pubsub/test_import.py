import pytest

from django.core.files.base import ContentFile
from import_export.formats.base_formats import XLSX
from model_bakery import baker
from pytest_mock import MockerFixture

from import_export_stomp.models import ImportJob
from import_export_stomp.pubsub import consumer
from tests.resources.fake_app.models import FakeModel
from tests.resources.fake_app.resources import FakeResource
from tests.utils import create_payload

XLSX_CONTENT_TYPE = XLSX.CONTENT_TYPE


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
        assert import_job.errors == ""

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
        assert import_job.job_status == "5/5 Import job finished"
        assert import_job.imported is not None
        assert import_job.errors == ""

        assert FakeModel.objects.count() == 2
        row_1, row_2 = FakeModel.objects.order_by("id").all()

        assert row_1.name == "name1"
        assert row_1.value == 1
        assert row_2.name == "name2"
        assert row_2.value == 2

    def test_should_replace_previous_errors_when_dry_run_finishes(self):
        import_job = baker.make(
            ImportJob,
            file=ContentFile(b"name,value\nname1,abc", name="import_csv.csv"),
            model="Test",
            format="text/csv",
            errors="error from a previous dry run",
        )

        payload, ack, nack = create_payload(
            {"action": "import", "dry_run": True, "job_id": str(import_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        import_job.refresh_from_db()
        assert import_job.job_status == "[Dry run] 5/5 Import job finished"
        assert import_job.errors.startswith("Line: 1 - ")
        assert "error from a previous dry run" not in import_job.errors

    @pytest.mark.parametrize(
        ("dry_run", "expected_status"),
        (
            (False, "Imported file has a wrong encoding"),
            (True, "[Dry run] Imported file has a wrong encoding"),
        ),
    )
    def test_should_save_error_when_file_has_wrong_encoding(
        self, dry_run, expected_status
    ):
        import_job = baker.make(
            ImportJob,
            file=ContentFile(b"name,value\nn\xe9,1", name="import_csv.csv"),
            model="Test",
            format="text/csv",
        )

        payload, ack, nack = create_payload(
            {"action": "import", "dry_run": dry_run, "job_id": str(import_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        import_job.refresh_from_db()
        assert import_job.job_status == expected_status
        assert import_job.errors.startswith("Imported file has a wrong encoding: ")
        assert import_job.imported is None
        assert FakeModel.objects.count() == 0

    def test_should_save_error_when_file_cannot_be_read(self):
        import_job = baker.make(
            ImportJob,
            file=ContentFile(b"not a spreadsheet", name="import_xlsx.xlsx"),
            model="Test",
            format=XLSX_CONTENT_TYPE,
        )

        payload, ack, nack = create_payload(
            {"action": "import", "dry_run": False, "job_id": str(import_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        import_job.refresh_from_db()
        assert import_job.job_status == "Error reading file"
        assert import_job.errors.startswith("Error reading file: ")
        assert import_job.imported is None
        assert FakeModel.objects.count() == 0

    @pytest.mark.parametrize(
        ("dry_run", "expected_status"),
        ((False, "Import error"), (True, "[Dry run] Import error")),
    )
    def test_should_save_error_when_import_fails(
        self, csv_file: ContentFile, dry_run, expected_status
    ):
        import_job = baker.make(
            ImportJob, file=csv_file, model="Unknown", format="text/csv"
        )

        payload, ack, nack = create_payload(
            {"action": "import", "dry_run": dry_run, "job_id": str(import_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        import_job.refresh_from_db()
        assert import_job.job_status == expected_status
        assert import_job.errors == "Import error 'Unknown'\n"
        assert import_job.imported is None
        assert FakeModel.objects.count() == 0

    def test_should_save_base_errors(
        self, csv_file: ContentFile, mocker: MockerFixture
    ):
        mocker.patch.object(
            FakeResource, "before_import", side_effect=Exception("before import failed")
        )
        import_job = baker.make(
            ImportJob, file=csv_file, model="Test", format="text/csv"
        )

        payload, ack, nack = create_payload(
            {"action": "import", "dry_run": True, "job_id": str(import_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        import_job.refresh_from_db()
        assert import_job.job_status == "[Dry run] 5/5 Import job finished"
        assert import_job.errors.startswith("\nbefore import failed\n")
        assert FakeModel.objects.count() == 0

    def test_should_show_invalid_rows_in_dry_run_summary(self):
        import_job = baker.make(
            ImportJob,
            file=ContentFile(
                b"name,value\n" + b"n" * 31 + b",1", name="import_csv.csv"
            ),
            model="Test",
            format="text/csv",
        )

        payload, ack, nack = create_payload(
            {"action": "import", "dry_run": True, "job_id": str(import_job.pk)}
        )

        consumer(payload)

        nack.assert_not_called()
        ack.assert_called_once()

        import_job.refresh_from_db()
        assert import_job.job_status == "[Dry run] 5/5 Import job finished"
        assert import_job.errors == ""
        summary = import_job.change_summary.read().decode("utf-8")
        assert "<td>row</td><td>errors</td><td>name</td><td>value</td>" in summary
        assert "<mark>name</mark><br>Ensure this value has at most 30" in summary
        assert FakeModel.objects.count() == 0
