from sys import modules
from typing import Any
from unittest import mock

import pytest

from import_export.resources import ModelResource

from import_export_stomp.models import ImportJob
from import_export_stomp.models.exportjob import ExportJob
from import_export_stomp.resources import ModelConfig
from import_export_stomp.resources import resource_importer
from tests.utils import create_payload


class SampleResource(ModelResource):
    class Meta:
        model = ImportJob


@pytest.fixture
def resource() -> SampleResource:
    return SampleResource


@pytest.mark.django_db
class TestModelConfig:
    def test_model_config_should_pass_when_resource_is_provided(
        self, resource: SampleResource
    ) -> None:
        app_label = "import_export_stomp"
        model_name = "ImportJob"

        config = ModelConfig(
            app_label=app_label, model_name=model_name, resource=resource
        )

        assert config.model == ImportJob
        assert isinstance(config.resource, SampleResource)

    @mock.patch("import_export_stomp.resources.modelresource_factory")
    def test_model_config_should_pass_with_none_resource(self, mocker: Any) -> None:
        app_label = "import_export_stomp"
        model_name = "ExportJob"

        config = ModelConfig(app_label=app_label, model_name=model_name, resource=None)

        assert config.model == ExportJob
        mocker.assert_called_once_with(ExportJob)


class TestResourceImporter:
    def test_should_import_module_from_string(self):
        imported = resource_importer("tests.utils.create_payload")

        assert "tests.utils" in modules.keys()
        assert imported() == create_payload

    def test_should_fail_to_import_inexisting_module(self):
        imported = resource_importer("fake.module.fake_function")

        with pytest.raises(ModuleNotFoundError):
            imported()
