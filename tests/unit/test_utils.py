import contextlib

import import_export
import pytest

from django.template import exceptions
from django.test import override_settings

from import_export_stomp.models.exportjob import ExportJob
from import_export_stomp.utils import build_html_and_text_message
from import_export_stomp.utils import get_export_job_mail_context
from import_export_stomp.utils import get_export_job_mail_subject
from import_export_stomp.utils import get_export_job_mail_template
from import_export_stomp.utils import get_formats
from import_export_stomp.utils import send_export_job_completion_mail


@pytest.fixture
def export_job():
    return ExportJob(
        app_label="import_export_stomp",
        model="MyModel",
        site_of_origin="http://example.com",
    )


def test_get_formats():
    CSV = import_export.formats.base_formats.CSV
    XLSX = import_export.formats.base_formats.XLSX
    with contextlib.suppress(ImportError):
        formats = get_formats()
        assert CSV in formats
        assert XLSX in formats


@override_settings(EXPORT_JOB_COMPLETION_MAIL_TEMPLATE="test_template.html")
def test_build_html_and_text_message():
    with contextlib.suppress(ImportError, exceptions.TemplateDoesNotExist):
        template_name = "test_template.html"
        context = {"key": "value"}
        html_message, text_message = build_html_and_text_message(template_name, context)
        assert "key" in html_message
        assert "value" in html_message
        assert "key" in text_message
        assert "value" in text_message


def test_get_export_job_mail_context(export_job):
    with contextlib.suppress(ImportError):
        context = get_export_job_mail_context(export_job)
        assert "app_label" in context
        assert "model" in context
        assert "link" in context
        assert context["app_label"] == "import_export_stomp"
        assert context["model"] == "MyModel"
        assert "http://example.com" in context["link"]


@override_settings(EXPORT_JOB_COMPLETION_MAIL_SUBJECT="Django: Export job completed")
def test_get_export_job_mail_subject():
    with contextlib.suppress(ImportError):
        subject = get_export_job_mail_subject()
        assert subject == "Django: Export job completed"


@override_settings(EXPORT_JOB_COMPLETION_MAIL_TEMPLATE="export_job_completion.html")
def test_get_export_job_mail_template():
    with contextlib.suppress(ImportError):
        template = get_export_job_mail_template()
        assert template == "export_job_completion.html"


def test_send_export_job_completion_mail(export_job, mocker):
    with contextlib.suppress(ImportError):
        mocker.patch("import_export_stomp.utils.send_mail")
        send_export_job_completion_mail(export_job)
        mocker.assert_called_once()
