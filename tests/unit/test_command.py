import django_stomp.management.commands.pubsub

from django.core.management import call_command
from pytest_mock import MockerFixture

from import_export_stomp.utils import IMPORT_EXPORT_STOMP_PROCESSING_QUEUE


class TestCommand:
    def test_should_call_command_with_parameters(self, mocker: MockerFixture):
        mocked_start_processing = mocker.patch.object(
            django_stomp.management.commands.pubsub, "start_processing"
        )
        call_command("pubsub")

        mocked_start_processing.assert_called_with(
            IMPORT_EXPORT_STOMP_PROCESSING_QUEUE, "import_export_stomp.pubsub.consumer"
        )
