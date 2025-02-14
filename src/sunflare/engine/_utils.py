from __future__ import annotations

from enum import Enum
from itertools import count
from typing import Literal, Union
from weakref import WeakValueDictionary

import zmq


class DocumentNames(str, Enum):
    """Mirror of event_model.DocumentNames, subclassed from str.

    Deprecated events are omitted.
    """

    stop = "stop"
    start = "start"
    descriptor = "descriptor"
    event = "event"
    datum = "datum"
    resource = "resource"
    event_page = "event_page"
    datum_page = "datum_page"
    stream_resource = "stream_resource"
    stream_datum = "stream_datum"


class SocketRegistry:
    def __init__(self) -> None:
        self._allowed_sigs = DocumentNames
        self._sockets: WeakValueDictionary[int, zmq.SyncSocket] = WeakValueDictionary()
        self._token_count = count()

    def connect(
        self, sig: Union[Literal["all"], DocumentNames], socket: zmq.SyncSocket
    ) -> None:
        if sig not in self._allowed_sigs and sig != "all":
            raise ValueError(f"Signal '{sig}' is not allowed.")
        token = next(self._token_count)
        self._sockets[token] = socket

    def disconnect(self, token: int) -> None:
        self._sockets.pop(token)

    def process(self, sig: DocumentNames) -> None:
        for socket in self._sockets.values():
            socket.send_string(sig)
