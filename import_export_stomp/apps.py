from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImportExportCeleryConfig(AppConfig):
    name = "import_export_stomp"
    verbose_name = _("Import Export Stomp")
