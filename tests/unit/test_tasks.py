import json

import pytest

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from model_bakery import baker

from import_export_stomp.models import ExportJob
from import_export_stomp.models import ImportJob
from import_export_stomp.tasks import change_job_status


@pytest.mark.django_db
class TestChangeJobStatus:
    @pytest.mark.parametrize(
        ("dry_run", "expected_status"),
        ((False, "Exporting row 1/1"), (True, "[Dry run] Exporting row 1/1")),
    )
    def test_should_save_only_job_status(self, dry_run, expected_status):
        export_job = baker.make(
            ExportJob,
            format="text/csv",
            app_label="fake_app",
            model="fakemodel",
            queryset=json.dumps(["1"]),
        )
        export_job.queryset = json.dumps(["1", "2"])

        with CaptureQueriesContext(connection) as queries:
            change_job_status(export_job, "export", "Exporting row 1/1", dry_run)

        updates = [q["sql"] for q in queries if q["sql"].startswith("UPDATE")]
        assert len(updates) == 1
        set_clause = updates[0].split(" SET ")[1].split(" WHERE ")[0]
        assert set_clause == f"\"job_status\" = '{expected_status}'"

        export_job.refresh_from_db()
        assert export_job.job_status == expected_status
        assert export_job.queryset == json.dumps(["1"])
        assert cache.get("export_job_status_%s" % export_job.pk) == expected_status

    def test_should_keep_import_job_errors_unsaved(self):
        import_job = baker.make(
            ImportJob, file="import.csv", model="Test", format="text/csv"
        )
        import_job.errors = "not saved by the status change"

        change_job_status(import_job, "import", "1/5 Import started", dry_run=True)

        import_job.refresh_from_db()
        assert import_job.job_status == "[Dry run] 1/5 Import started"
        assert import_job.errors == ""
        assert (
            cache.get("import_job_status_%s" % import_job.pk)
            == "[Dry run] 1/5 Import started"
        )
