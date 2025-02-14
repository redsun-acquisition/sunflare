from __future__ import annotations

from itertools import count
from typing import TYPE_CHECKING, Literal, Union
from weakref import WeakValueDictionary

from event_model import (
    Datum,
    DatumPage,
    Event,
    EventDescriptor,
    EventPage,
    Resource,
    RunStart,
    RunStop,
    StreamDatum,
    StreamResource,
)

from sunflare.virtual import encode

if TYPE_CHECKING:
    import zmq

DocumentType = Union[
    Datum,
    DatumPage,
    Event,
    EventDescriptor,
    EventPage,
    Resource,
    RunStart,
    RunStop,
    StreamDatum,
    StreamResource,
]
AllowedSigs = Literal["all", "start", "descriptor", "event", "stop"]


class SocketRegistry:
    """A registry for ZMQ sockets."""

    def __init__(self) -> None:
        self._allowed_sigs = {"start", "descriptor", "event", "stop"}
        self._sockets: WeakValueDictionary[int, zmq.Socket[bytes]] = (
            WeakValueDictionary()
        )
        self._token_count = count()

    def connect(
        self,
        sig: AllowedSigs,
        socket: zmq.Socket[bytes],
    ) -> int:
        """Connect a socket to the registry.

        Parameters
        ----------
        sig : ``"all" | "start" | "descriptor" | "event" | "stop"``
            The signal to connect to. Defaults to ``"all"``.
        socket : ``zmq.Socket[bytes]``
            The socket to connect.

        Returns
        -------
        ``int``
            The token representing the connection.

        Raises
        ------
        ``ValueError``
            If the signal value is not allowed.
        """
        if not any(sig == "all" or sig == s for s in self._allowed_sigs):
            raise ValueError(f"Signal '{sig}' is not allowed.")
        token = next(self._token_count)
        self._sockets[token] = socket
        return token

    def disconnect(self, token: int) -> None:
        """Disconnect a socket from the registry.

        Parameters
        ----------
        token : ``int``
            The token representing the connection.
        """
        self._sockets.pop(token)

    def process(self, sig: str, doc: DocumentType) -> None:
        """Process a signal.

        All connected sockets will send an
        encoded
        """
        for socket in self._sockets.values():
            socket.send_multipart([sig.encode(), encode(doc)])
