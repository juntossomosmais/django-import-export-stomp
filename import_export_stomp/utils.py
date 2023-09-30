from django.conf import settings
from import_export.formats.base_formats import DEFAULT_FORMATS

IMPORT_EXPORT_STOMP_EXCLUDED_FORMATS = getattr(
    settings,
    "IMPORT_EXPORT_STOMP_EXCLUDED_FORMATS",
    [],
)


def get_formats():
    return [
        format
        for format in DEFAULT_FORMATS
        if format.TABLIB_MODULE.split(".")[-1].strip("_")
        not in IMPORT_EXPORT_STOMP_EXCLUDED_FORMATS
    ]
