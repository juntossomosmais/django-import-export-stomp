import logging

from typing import Optional

from django.apps import apps
from import_export.resources import Resource
from import_export.resources import modelresource_factory

logger = logging.getLogger(__name__)


class ModelConfig:
    resource: Resource

    def __init__(
        self,
        app_label: Optional[str] = None,
        model_name: Optional[str] = None,
        resource: Optional[Resource] = None,
    ):
        self.model = apps.get_model(app_label=app_label, model_name=model_name)
        logger.debug(resource)
        if resource:
            self.resource = resource()
        else:
            self.resource = modelresource_factory(self.model)
