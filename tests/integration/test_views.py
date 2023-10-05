import json

from datetime import datetime
from http import HTTPStatus
from unittest.mock import ANY

import pytest

from django.contrib import auth
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from model_bakery import baker
from pytest_django.fixtures import SettingsWrapper
from pytest_mock import MockerFixture

from import_export_stomp.views import util

FILENAME = "csv.csv"
APPLICATION_JSON = "application/json"


@pytest.mark.django_db
class TestGeneratePresignedPost:
    @pytest.fixture
    def client(self) -> Client:
        user = baker.make(User, is_staff=True, is_superuser=True)
        client = Client(enforce_csrf_checks=False)
        client.force_login(user)

        assert auth.get_user(client).is_authenticated

        return client

    @pytest.fixture
    def endpoint(self) -> str:
        return reverse("import_export_stomp_presigned_url")

    @pytest.mark.parametrize(
        "http_method", ("GET", "OPTIONS", "PUT", "DELETE", "PATCH")
    )
    def test_should_fail_if_not_post(
        self, client: Client, endpoint: str, http_method: str
    ):
        request_fn = getattr(client, http_method.lower())
        response = request_fn(endpoint)
        assert response.status_code != HTTPStatus.CREATED

    def test_should_fail_if_user_is_not_staff(self, client: Client, endpoint: str):
        User.objects.all().update(is_staff=False)
        response = client.post(endpoint)

        assert response.status_code == HTTPStatus.FOUND
        assert "/admin/login" in response.url

    def test_should_fail_if_content_type_is_not_a_valid_spreadsheet(
        self, client: Client, endpoint: str
    ):
        response = client.post(
            endpoint,
            content_type=APPLICATION_JSON,
            data=json.dumps({"filename": FILENAME, "mimetype": "application/fake"}),
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {
            "error": "File format application/fake is not allowed. Accepted formats: "
            "['text/csv', 'application/vnd.ms-excel', "
            "'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
            ", 'text/tab-separated-values', 'application/vnd.oasis.opendocument.spreadsheet', 'application/json', "
            "'text/yaml', 'text/html']"
        }

    def test_should_fail_if_module_is_not_present(
        self,
        client: Client,
        endpoint: str,
        mocker: MockerFixture,
    ):
        mocker.patch.object(util, "find_spec", return_value=None)

        response = client.post(
            endpoint,
            content_type=APPLICATION_JSON,
            data=json.dumps({"filename": FILENAME, "mimetype": "text/csv"}),
        )

        assert response.status_code == HTTPStatus.FAILED_DEPENDENCY
        assert response.json() == {
            "error": "boto3 and django-storages required for this action."
        }

    def test_should_return_presigned_info(
        self, settings: SettingsWrapper, client: Client, endpoint: str
    ):
        response = client.post(
            endpoint,
            content_type=APPLICATION_JSON,
            data=json.dumps({"filename": FILENAME, "mimetype": "text/csv"}),
        )

        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {
            "url": "http://minio:9000/example",
            "fields": {
                "key": settings.IMPORT_EXPORT_STOMP_PRESIGNED_FOLDER + FILENAME,
                "x-amz-algorithm": "AWS4-HMAC-SHA256",
                "x-amz-credential": f"minioadmin/{datetime.now().strftime('%Y%m%d')}/us-east-1/s3/aws4_request",
                "x-amz-date": ANY,
                "policy": ANY,
                "x-amz-signature": ANY,
            },
        }
