import logging

from django.apps import apps
from import_export.resources import modelresource_factory

logger = logging.getLogger(__name__)


class ModelConfig:
    def __init__(self, app_label=None, model_name=None, resource=None):
        self.model = apps.get_model(app_label=app_label, model_name=model_name)
        logger.debug(resource)
        if resource:
            self.resource = resource()
        else:
            self.resource = modelresource_factory(self.model)
