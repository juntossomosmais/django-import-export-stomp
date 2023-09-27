import contextlib

from django.apps import apps

from import_export_stomp.apps import ImportExportStompConfig


class TestApps:
    def test_import_export_stomp_app_config(self):
        with contextlib.suppress(LookupError):
            app_config = apps.get_app_config("import_export_stomp")

            assert isinstance(app_config, ImportExportStompConfig)
            assert app_config.name == "import_export_stomp"
            assert app_config.verbose_name == "Import Export Stomp"
