import contextlib

import import_export
import pytest

from import_export_stomp.utils import get_formats


@pytest.mark.django_db
class TestUtils:
    def test_get_formats(self) -> None:
        CSV = import_export.formats.base_formats.CSV
        XLSX = import_export.formats.base_formats.XLSX
        with contextlib.suppress(ImportError):
            formats = get_formats()
            assert CSV in formats
            assert XLSX in formats
