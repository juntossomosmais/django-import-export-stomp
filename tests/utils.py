from typing import Dict
from typing import Tuple
from unittest.mock import MagicMock

from django_stomp.services.consumer import Payload


def create_payload(
    body: Dict = None, headers: Dict = None
) -> Tuple[Payload, MagicMock, MagicMock]:
    ack = MagicMock()
    nack = MagicMock()
    return (
        Payload(ack=ack, nack=nack, body=body or {}, headers=headers or {}),
        ack,
        nack,
    )
