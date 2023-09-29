import contextlib

from unittest.mock import Mock
from unittest.mock import patch

import import_export
import pytest

from django.test import override_settings

from import_export_stomp.models.exportjob import ExportJob
from import_export_stomp.utils import build_html_and_text_message
from import_export_stomp.utils import get_export_job_mail_context
from import_export_stomp.utils import get_export_job_mail_subject
from import_export_stomp.utils import get_export_job_mail_template
from import_export_stomp.utils import get_formats
from import_export_stomp.utils import send_export_job_completion_mail


@pytest.fixture
def export_job_mail():
    return Mock(
        updated_by=Mock(email="test@example.com"),
    )


@pytest.fixture
def export_job():
    return ExportJob(
        app_label="import_export_stomp",
        model="MyModel",
        site_of_origin="http://example.com",
    )


@pytest.fixture
def mock_get_template():
    def mock_template_render(template_name, context=None):
        class MockTemplate:
            def render(self, context):
                return (
                    f"HTML content for {template_name}",
                    f"Text content for {template_name}",
                )

        return MockTemplate()

    return mock_template_render


@pytest.mark.django_db
class TestUtils:
    def test_get_formats(self):
        CSV = import_export.formats.base_formats.CSV
        XLSX = import_export.formats.base_formats.XLSX
        with contextlib.suppress(ImportError):
            formats = get_formats()
            assert CSV in formats
            assert XLSX in formats

    @override_settings(EXPORT_JOB_COMPLETION_MAIL_TEMPLATE="test_template.html")
    @patch("import_export_stomp.utils.get_template")
    def test_build_html_and_text_message(self, mock_get_template):
        template_name = "test_template.html"
        context = {"key": "value"}

        _, _ = build_html_and_text_message(template_name, context)

        mock_get_template.assert_called_once_with(template_name)

    def test_get_export_job_mail_context(self, export_job):
        with contextlib.suppress(ImportError):
            context = get_export_job_mail_context(export_job)
            assert "app_label" in context
            assert "model" in context
            assert "link" in context
            assert context["app_label"] == "import_export_stomp"
            assert context["model"] == "MyModel"
            assert "http://example.com" in context["link"]

    @override_settings(
        EXPORT_JOB_COMPLETION_MAIL_SUBJECT="Django: Export job completed"
    )
    def test_get_export_job_mail_subject(self):
        with contextlib.suppress(ImportError):
            subject = get_export_job_mail_subject()
            assert subject == "Django: Export job completed"

    @override_settings(EXPORT_JOB_COMPLETION_MAIL_TEMPLATE="export_job_completion.html")
    def test_get_export_job_mail_template(self):
        with contextlib.suppress(ImportError):
            template = get_export_job_mail_template()
            assert template == "export_job_completion.html"

    @patch("import_export_stomp.utils.send_mail")
    @patch(
        "import_export_stomp.utils.build_html_and_text_message",
        return_value=("HTML Message", "Text Message"),
    )
    @patch(
        "import_export_stomp.utils.get_export_job_mail_context",
        return_value={"context_key": "context_value"},
    )
    @patch(
        "import_export_stomp.utils.get_export_job_mail_template",
        return_value="test_template.html",
    )
    @patch(
        "import_export_stomp.utils.get_export_job_mail_subject",
        return_value="Test Subject",
    )
    def test_send_export_job_completion_mail(
        self,
        mock_subject,
        mock_template,
        mock_context,
        mock_message,
        mock_send_mail,
        export_job_mail,
    ):
        send_export_job_completion_mail(export_job_mail)

        mock_subject.assert_called_once()
        mock_template.assert_called_once()
        mock_context.assert_called_once_with(export_job_mail)
        mock_message.assert_called_once_with(
            "test_template.html",
            {"context_key": "context_value", "export_job": export_job_mail},
        )
        mock_send_mail.assert_called_once_with(
            subject="Test Subject",
            message="Text Message",
            html_message="HTML Message",
            from_email="root@localhost",
            recipient_list=["test@example.com"],
        )
