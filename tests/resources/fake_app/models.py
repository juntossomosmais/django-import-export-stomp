from django.db import models

from import_export_stomp.utils import resource_importer


class FakeModel(models.Model):
    name = models.CharField(max_length=30)
    value = models.IntegerField(default=0)

    @classmethod
    def export_resource_classes(cls):
        return {
            "FakeResource": (
                "FakeModel resource",
                resource_importer("tests.resources.fake_app.resources.FakeResource")(),
            ),
        }
