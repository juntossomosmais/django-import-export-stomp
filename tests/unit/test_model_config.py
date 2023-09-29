from unittest import mock

import pytest

from import_export.resources import ModelResource

from import_export_stomp.model_config import ModelConfig
from import_export_stomp.models import ImportJob
from import_export_stomp.models.exportjob import ExportJob


class SampleResource(ModelResource):
    class Meta:
        model = ImportJob


@pytest.fixture
def resource():
    return SampleResource


@pytest.mark.django_db
class TestModelConfig:
    def test_model_config_should_pass_when_resource_is_provided(self, resource):
        app_label = "import_export_stomp"
        model_name = "ImportJob"

        config = ModelConfig(
            app_label=app_label, model_name=model_name, resource=resource
        )

        assert config.model == ImportJob
        assert isinstance(config.resource, SampleResource)

    @mock.patch("import_export_stomp.model_config.modelresource_factory")
    def test_model_config_should_pass_with_none_resource(self, mocker):
        app_label = "import_export_stomp"
        model_name = "ExportJob"

        config = ModelConfig(app_label=app_label, model_name=model_name, resource=None)

        assert config.model == ExportJob
        mocker.assert_called_once_with(ExportJob)
