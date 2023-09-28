from import_export_stomp.apps import ImportExportStompConfig


class TestApps:
    def test_import_export_stomp_app_config(self):
        app_name = "import_export_stomp"
        app_verbose_name = "Import Export Stomp"
        app_config = ImportExportStompConfig

        assert app_config.name == app_name
        assert app_config.verbose_name == app_verbose_name
