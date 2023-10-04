from import_export import resources

from tests.resources.fake_app.models import FakeModel


class FakeResource(resources.ModelResource):
    class Meta:
        model = FakeModel
        fields = ("name", "value")
        import_id_fields = ("name",)
