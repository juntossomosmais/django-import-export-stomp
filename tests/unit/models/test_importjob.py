import os

import pytest

from django.utils import timezone

from import_export_stomp.models import ImportJob


@pytest.fixture
def import_job():
    return ImportJob(file="test.csv", model="TestModel", format="CSV")


@pytest.mark.django_db
class TestImportJobModel:
    def test_import_job_model(self, import_job):
        import_job.save()

        assert import_job.file == "test.csv"
        assert import_job.format == "CSV"
        assert import_job.model == "TestModel"

        import_job.processing_initiated = timezone.now()
        import_job.job_status = "Processing"
        import_job.save()

        assert import_job.processing_initiated is not None
        assert import_job.job_status == "Processing"

        format_choices = import_job.get_format_choices()
        assert len(format_choices) > 0
        assert all(isinstance(choice, tuple) for choice in format_choices)

    def test_importjob_post_save(self, import_job):
        import_job.save()

        import_job_db = ImportJob.objects.get(pk=import_job.pk)

        assert import_job_db.processing_initiated is not None

    def test_auto_delete_file_on_delete(self, import_job):
        import_job.save()

        file_path = import_job.file.path

        import_job.delete()

        assert not os.path.exists(file_path)
        assert not ImportJob.objects.filter(pk=import_job.pk).exists()
