from unittest.mock import Mock

import pytest

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User

from import_export_stomp import admin_actions
from import_export_stomp.admin import ImportJobAdmin
from import_export_stomp.models import ImportJob
from import_export_stomp.tasks import run_import_job


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture
def import_job(user):
    return ImportJob.objects.create(
        model="ModelTest",
        file="test.csv",
        change_summary="Summary",
        imported=True,
        author=user,
        updated_by=user,
    )


@pytest.mark.django_db
def test_run_import_job_action(admin_site, import_job, user):
    admin = ImportJobAdmin(ImportJob, admin_site)

    request = Mock(user=user)

    admin_actions.run_import_job_action(
        modeladmin=admin, request=request, queryset=[ImportJob.objects.all()]
    )

    run_import_job.delay.assert_called_once_with(import_job.pk, dry_run=False)
