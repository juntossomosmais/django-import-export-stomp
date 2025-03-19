from argparse import ArgumentParser

from django_stomp.management.commands.pubsub import Command as PubsubCommand

from import_export_stomp.utils import IMPORT_EXPORT_STOMP_PROCESSING_QUEUE


class Command(PubsubCommand):
    help = "Listens to queue to process messages"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        This method is empty to remove required django-stomp parameters
        """

    def handle(self, *args, **options):
        super().handle(
            *args,
            **{
                "source_destination": IMPORT_EXPORT_STOMP_PROCESSING_QUEUE,
                "callback_function": "import_export_stomp.pubsub.consumer",
            },
        )
