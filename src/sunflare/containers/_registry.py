from __future__ import annotations

from typing import Callable, Iterable, TypeGuard, overload

from bluesky.utils import MsgGenerator  # noqa: TC002

from sunflare.controller import ControllerProtocol
from sunflare.model import ModelProtocol

#: Registry for storing model protocols
#: The dictionary maps the protocol owners (usually Controller plugins) to a set of `ModelProtocol` types.
protocol_registry: dict[str, set[type[ModelProtocol]]] = {}

#: Registry for storing plan generators
#: The dictionary maps plan owners (usually Controller plugins) to a Bluesky generator function.
plan_registry: dict[str, Callable[..., MsgGenerator]] = {}


def _is_model_protocol(proto: type) -> TypeGuard[type[ModelProtocol]]:
    """Type guard to check if a type implements ModelProtocol."""
    return ModelProtocol in proto.mro()


@overload
def register_protocols(
    owner: ControllerProtocol, protocols: type[ModelProtocol]
) -> None: ...
@overload
def register_protocols(
    owner: ControllerProtocol, protocols: Iterable[type[ModelProtocol]]
) -> None: ...
def register_protocols(
    owner: ControllerProtocol,
    protocols: type[ModelProtocol] | Iterable[type[ModelProtocol]],
) -> None:
    """Register one or multiple protocols.

    Parameters
    ----------
    owner : ``ControllerProtocol``
        The owner of the protocol.
    protocols : ``type[ModelProtocol] | Iterable[type[ModelProtocol]]``
        The protocol or protocols to register. They must be subclasses of `ModelProtocol`.

    Raises
    ------
    TypeError
        If the owner does not implement `ControllerProtocol`
        or if the protocols are not subclasses of `ModelProtocol`.
    """
    if not isinstance(owner, ControllerProtocol):
        raise TypeError(f"Owner must implement ControllerProtocol, got {type(owner)}")

    # Handle both single protocol and iterable of protocols
    if isinstance(protocols, type):
        protos = {protocols}
    else:
        protos = set(protocols)

    # Use type guard for safe protocol checking
    if not all(_is_model_protocol(proto) for proto in protos):
        raise TypeError("All protocols must be subclasses of ModelProtocol")

    owner_name = owner.__class__.__name__
    if owner_name not in protocol_registry:
        protocol_registry[owner_name] = set()
    protocol_registry[owner_name].update(protos)
