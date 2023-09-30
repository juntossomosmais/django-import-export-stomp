from django.conf import settings
from django.core.files.storage import get_storage_class
from django.test import override_settings

from import_export_stomp.fields import ImportExportFileField


class TestFields:
    @override_settings(
        IMPORT_EXPORT_STOMP_STORAGE="django.core.files.storage.FileSystemStorage"
    )
    def test_import_export_file_field_custom_storage(self):
        field = ImportExportFileField()

        storage_class = get_storage_class(settings.IMPORT_EXPORT_STOMP_STORAGE)

        assert isinstance(field.storage, storage_class)
