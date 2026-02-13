from __future__ import annotations

from typing import Any

from bluesky.protocols import Configurable, HasName, HasParent
from typing_extensions import Protocol, runtime_checkable

__all__ = ["PDevice"]


@runtime_checkable
class PDevice(HasName, HasParent, Configurable[Any], Protocol):  # pragma: no cover
    """Minimal required protocol for a recognizable device in Redsun.

    Exposes the following Bluesky protocols:

    - [`bluesky.protocols.HasName`]()
    - [`bluesky.protocols.HasParent`]()
    - [`bluesky.protocols.Configurable`]()

    Devices should implement their configuration properties directly
    and provide implementations of `describe_configuration()` and
    `read_configuration()` methods as required by the Configurable protocol.
    """
