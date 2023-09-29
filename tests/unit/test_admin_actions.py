from unittest.mock import Mock

import pytest

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User

from import_export_stomp.admin import ImportJobAdmin
from import_export_stomp.admin_actions import run_export_job_action
from import_export_stomp.models import ExportJob


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture
def export_job(user):
    return ExportJob.objects.create(
        app_label="app_label",
        model="model",
        queryset="[]",
        site_of_origin="http://example.com",
    )


@pytest.mark.django_db
def test_run_export_job_action(admin_site, export_job, user):
    admin = ImportJobAdmin(ExportJob, admin_site)

    request = Mock(user=user)

    with pytest.raises(Exception):
        run_export_job_action(modeladmin=admin, request=request, queryset=[export_job])
