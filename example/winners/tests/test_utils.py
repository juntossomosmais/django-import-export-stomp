from django.test import TestCase
from django.test import override_settings
from import_export_celery.models import ExportJob
from import_export_celery.utils import DEFAULT_EXPORT_JOB_COMPLETION_MAIL_SUBJECT
from import_export_celery.utils import DEFAULT_EXPORT_JOB_COMPLETION_MAIL_TEMPLATE
from import_export_celery.utils import get_export_job_mail_context
from import_export_celery.utils import get_export_job_mail_subject
from import_export_celery.utils import get_export_job_mail_template


class UtilsTestCases(TestCase):
    def test_get_export_job_mail_subject_by_default(self):
        self.assertEqual(
            DEFAULT_EXPORT_JOB_COMPLETION_MAIL_SUBJECT, get_export_job_mail_subject()
        )

    @override_settings(EXPORT_JOB_COMPLETION_MAIL_SUBJECT="New subject")
    def test_get_export_job_mail_subject_overridden(self):
        self.assertEqual("New subject", get_export_job_mail_subject())

    def test_get_export_job_mail_template_default(self):
        self.assertEqual(
            DEFAULT_EXPORT_JOB_COMPLETION_MAIL_TEMPLATE, get_export_job_mail_template()
        )

    @override_settings(EXPORT_JOB_COMPLETION_MAIL_TEMPLATE="mytemplate.html")
    def test_get_export_job_mail_template_overridden(self):
        self.assertEqual("mytemplate.html", get_export_job_mail_template())

    def test_get_export_job_mail_context(self):
        export_job = ExportJob.objects.create(
            app_label="winners", model="Winner", site_of_origin="http://127.0.0.1:8000"
        )
        context = get_export_job_mail_context(export_job)
        expected_context = {
            "app_label": "winners",
            "model": "Winner",
            "link": f"http://127.0.0.1:8000/adminimport_export_celery/exportjob/{export_job.id}/change/",  # noqa
        }
        self.assertEqual(context, expected_context)
