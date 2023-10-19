from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImportExportStompConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "import_export_stomp"
    verbose_name = _("Import Export Stomp")
