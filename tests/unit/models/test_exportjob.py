import json

from unittest.mock import Mock
from unittest.mock import patch

import pytest

from import_export_stomp.models.exportjob import ExportJob


@pytest.fixture
def export_job():
    return ExportJob(
        app_label="import_export_stomp",
        model="ImportJob",
        queryset=json.dumps([1, 2, 3]),
        site_of_origin="http://example.com",
    )


@pytest.mark.django_db
class TestExportJobModel:
    def test_exportjob_post_save_signal_handler(self):
        export_job = ExportJob(
            file="test_file.csv", format="CSV", resource="TestResource"
        )
        export_job.save()

        assert export_job.processing_initiated is not None

    def test_get_content_type(self, export_job):
        with patch(
            "import_export_stomp.models.exportjob.ContentType.objects.get"
        ) as mock_get_content_type:
            content_type = export_job.get_content_type()

        mock_get_content_type.assert_called_once_with(
            app_label=export_job.app_label,
            model=export_job.model,
        )
        assert content_type is mock_get_content_type.return_value

    def test_get_queryset_custom_resource(self, export_job):
        export_job.resource = "sample_resource"

        with patch.object(
            export_job, "get_resource_class"
        ) as mock_get_resource_class, patch.object(export_job, "get_content_type"):
            mock_resource = Mock(
                get_export_queryset=Mock(return_value=Mock(filter=Mock()))
            )
            mock_get_resource_class.return_value = mock_resource

            export_job.get_queryset()

        mock_get_resource_class.assert_called_once()

    def test_get_queryset_default_resource(self, export_job):
        export_job.resource = ""
        with patch(
            "import_export_stomp.models.exportjob.ExportJob.get_resource_class"
        ) as mock_get_resource_class, patch(
            "import_export_stomp.models.exportjob.ExportJob.get_content_type"
        ) as mock_get_content_type:
            mock_get_resource_class.return_value = None
            mock_content_type = Mock(model_class=Mock(objects=Mock(filter=Mock())))
            mock_get_content_type.return_value = mock_content_type

            export_job.get_queryset()

        mock_get_resource_class.assert_called_once()
        mock_get_content_type.assert_called_once()
