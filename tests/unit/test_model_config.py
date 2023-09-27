import contextlib

import pytest

from import_export.resources import ModelResource

from import_export_stomp.model_config import ModelConfig
from import_export_stomp.models import ImportJob


class SampleResource(ModelResource):
    class Meta:
        model = ImportJob


@pytest.fixture
def sample_resource():
    return SampleResource()


@pytest.mark.django_db
class TestModelConfig:
    def test_model_config_instance(self, sample_resource):
        with contextlib.suppress(LookupError):
            app_label = "import_export_stomp"
            model_name = "ImportJob"

            config = ModelConfig(
                app_label=app_label, model_name=model_name, resource=sample_resource
            )

            assert config.model == ImportJob
            assert isinstance(config.resource, SampleResource)
