"""Wrapper for the :class:`~bluesky.run_engine.RunEngine` class to allow execution without blocking the main thread.

The original implementation of the ``RunEngine`` blocks the
execution of the main thread when the ``__call__`` method is used.
This wrapper uses a ``ThreadPoolExecutor`` to run the execution
in a separate thread, allowing the main thread to continue executing other tasks.

.. note::

    The ``context_manager`` attribute is forced to be an empty list to
    avoid the use of the built-in ``SignalHandler`` context manager.
    The rationale is that the original implementation is meant
    for interactive usage (e.g., Jupyter notebooks, scripts) and not for
    applications relying on an event loop.

    When invoking ``RunEngine.__call__`` not in the main thread,
    this will cause an exception as in Python
    signal handlers (e.g. ``SIGINT``) can not
    be handled in threads other than the main thread.
"""

from __future__ import annotations

import asyncio
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from itertools import count
from typing import Any, Callable, Generic, TypeVar, Union, cast, overload

import zmq
from bluesky.run_engine import (
    Dispatcher as BlueskyDispatcher,
)
from bluesky.run_engine import (
    RunEngine as BlueskyRunEngine,
)
from bluesky.run_engine import RunEngineResult
from event_model import DocumentNames

from sunflare.engine._utils import AllowedSigs, DocumentType, SocketRegistry

__all__ = ["RunEngine", "RunEngineResult"]


class CallableToken(int):
    """Helper class to generate unique tokens for function subscriptions."""

    ...


class SocketToken(int):
    """Helper class to generate unique tokens for socket subscriptions."""

    ...


T = TypeVar("T", bound=int)


class TokenGenerator(Generic[T]):
    """Custom generator for unique tokens.

    Helps differentiate between function and socket tokens.
    """

    def __init__(self, token_type: type[T]) -> None:
        self._count = count()
        self._token_type = token_type

    def __iter__(self) -> TokenGenerator[T]:
        return self

    def __next__(self) -> T:
        return self._token_type(next(self._count))


REResultType = Union[RunEngineResult, tuple[str, ...]]
FuncSocket = Union[Callable[[str, dict[str, Any]], None], zmq.Socket[bytes]]
Token = Union[CallableToken, SocketToken]


class RunEngine(BlueskyRunEngine):
    __doc__ = BlueskyRunEngine.__doc__

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # force the context_managers to be empty,
        # otherwise the RunEngine will try to use the
        # SignalHandler context manager
        kwargs["context_managers"] = []
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._result: REResultType
        super().__init__(*args, **kwargs)  # type: ignore[no-untyped-call]

        # override pause message to be an empty string
        self.pause_msg = ""

        # Python 3.9 explicitly requires the event loop to be set
        # when running in a separate thread
        if sys.version_info < (3, 10):
            self._run_in_executor = self.__run_in_executor_explicit
        else:
            self._run_in_executor = self.__run_in_executor

        # override the original dispatcher with our own
        self.dispatcher = Dispatcher()

        # aliases for back-compatibility
        self.subscribe_lossless = self.dispatcher.subscribe
        self.unsubscribe_lossless = self.dispatcher.unsubscribe
        self._subscribe_lossless = self.dispatcher.subscribe
        self._unsubscribe_lossless = self.dispatcher.unsubscribe

    def subscribe(self, func_or_socket: FuncSocket, name: str = "all") -> Token:
        """Subscribe a callback function or a ZMQ socket to the engine.

        Sockets are called before the callback functions.

        For callback functions, the expected signature is:

        .. code-block:: python

            def callback(name: str, doc: dict) -> None: ...

        Parameters
        ----------
        func_or_socket : ``Callable[[str, object], None] | zmq.Socket[bytes]``
            The callback function or ZMQ socket to subscribe.
        name : ``str``, optional
            The name of the document type to subscribe to. Defaults to "all".

        Returns
        -------
        ``CallableToken | SocketToken``
            The token to use for unsubscribing from the engine.
        """
        # our custom dispatcher should have
        # the return type correctly hinted,
        # but mypy complains about it and
        # thinks that we're returning Any;
        # we suppress it for now
        return self.dispatcher.subscribe(func_or_socket, name)  # type: ignore[no-untyped-call,no-any-return]

    def unsubscribe(self, token: Token) -> None:
        """Unsubscribe a callback function or a ZMQ socket from the engine.

        Parameters
        ----------
        token: ``CallableToken | SocketToken``
            The token to unsubscribe from the engine.
        """
        self.dispatcher.unsubscribe(token)  # type: ignore[no-untyped-call]

    def __run_in_executor_explicit(self, *args: Any, **kwargs: Any) -> REResultType:
        asyncio.set_event_loop(self.loop)
        return super().__call__(*args, **kwargs)  # type: ignore[no-any-return,no-untyped-call]

    def __run_in_executor(self, *args: Any, **kwargs: Any) -> REResultType:
        return super().__call__(*args, **kwargs)  # type: ignore[no-any-return,no-untyped-call]

    def __call__(self, *args: Any, **metadata_kw: Any) -> Future[REResultType]:
        self._fut = self._executor.submit(
            lambda: self._run_in_executor(*args, **metadata_kw)
        )
        self._fut.add_done_callback(self._set_result)
        return self._fut

    def _set_result(self, fut: Future[REResultType]) -> None:
        self._result = fut.result()

    @property
    def result(self) -> Union[REResultType]:
        return self._result


class Dispatcher(BlueskyDispatcher):
    """Subclass of the original bluesky Dispatcher to host a socket registry.

    This version implements a secondary registry to keep track of
    the sockets used for the subscriptions. This is necessary to allow
    the unsubscription of sockets when the user decides to unsubscribe
    from a specific socket (or all sockets).

    The socket registry keeps weak references to the sockets to avoid
    memory leaks when the sockets are no longer used.
    """

    def __init__(self) -> None:
        super().__init__()  # type: ignore[no-untyped-call]
        self.socket_registry = SocketRegistry()

        # override the original _counter
        # with our own TokenGenerator
        self._counter = TokenGenerator(CallableToken)  # type: ignore[assignment]
        self._socket_counter = TokenGenerator(SocketToken)
        self._socket_token_mapping: dict[SocketToken, list[int]] = {}

    def process(self, name: str, doc: DocumentType) -> None:
        """Process a document by dispatching it to the subscribed callbacks.

        Documents are first emitted on registered ZMQ sockets before
        being dispatched to the callback functions.

        Parameters
        ----------
        name : ``str``
            The name of the document type.
        doc : ``dict``
            The document to dispatch.
        """
        self.socket_registry.process(name, doc)
        super().process(name, doc)  # type: ignore[no-untyped-call]

    @overload
    def subscribe(
        self, func_or_socket: zmq.Socket[bytes], name: AllowedSigs = "all"
    ) -> SocketToken: ...

    @overload
    def subscribe(
        self,
        func_or_socket: Callable[[str, dict[str, Any]], None],
        name: AllowedSigs = "all",
    ) -> CallableToken: ...

    def subscribe(self, func_or_socket: FuncSocket, name: AllowedSigs = "all") -> Token:
        """Register a callback function or a ZMQ socket to dispatch documents.

        For callback functions, the expected signature is:

        .. code-block:: python

            def callback(name: str, doc: dict) -> None: ...

        Parameters
        ----------
        func_or_socket : ``zmq.Socket[bytes] | Callable[[str, object], None]``
            The callback function or ZMQ socket to register.
        name : ``'all' | 'start' | 'descriptor' | 'event' | 'stop'``, optional
            The name of the document type to subscribe to. Defaults to "all".

        Returns
        -------
        ``CallableToken | SocketToken``
            The token to use for unsubscribing from the dispatcher.

            - If a callback function is subscribed, the token is a ``CallableToken``.
            - If a ZMQ socket is subscribed, the token is a ``SocketToken``.
        """
        if isinstance(func_or_socket, zmq.Socket):
            private_tokens: list[int] = []
            if name == "all":
                for key in DocumentNames:
                    private_tokens.append(
                        self.socket_registry.connect(key, func_or_socket)
                    )
            else:
                name = DocumentNames[name]
                private_tokens = [self.socket_registry.connect(name, func_or_socket)]
            public_token = next(self._socket_counter)
            self._socket_token_mapping[public_token] = private_tokens
            return public_token
        else:
            # we don't have control over the original implementation;
            # casting is the best we can do;
            # at runtime the effective type will be CallableToken anyway
            # because we're overriding the _counter attribute
            return cast(CallableToken, super().subscribe(func_or_socket, name))  # type: ignore[no-untyped-call]

    @overload
    def unsubscribe(self, token: SocketToken) -> None: ...

    @overload
    def unsubscribe(self, token: CallableToken) -> None: ...

    def unsubscribe(self, token: Token) -> None:
        """Unsubscribe a previously registered callback function or ZMQ socket.

        Parameters
        ----------
        token: ``SocketToken | CallableToken``
            The token to unsubscribe from the dispatcher.
        """
        if isinstance(token, SocketToken):
            for private_token in self._socket_token_mapping.pop(token, []):
                self.socket_registry.disconnect(private_token)
        else:
            super().unsubscribe(token)  # type: ignore[no-untyped-call]

    def unsubscribe_all(self) -> None:
        """Unsubscribe all registered callback functions and ZMQ sockets."""
        for public_token in self._socket_token_mapping.keys():
            self.unsubscribe(public_token)
        super().unsubscribe_all()  # type: ignore[no-untyped-call]
