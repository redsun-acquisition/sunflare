from __future__ import annotations

import inspect
from typing import (
    Any,
    Callable,
    Iterable,
    TypeGuard,
    get_type_hints,
    overload,
)

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


def get_signature_info(obj: Callable) -> dict[str, Any]:
    """Extract signature information from a callable object.

    Parameters
    ----------
    obj : Callable
        The callable object to inspect.
        Callable objects can be functions, class methods,
        or classes with a ``__call__`` method.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the signature information,
        including the function name, parameters, and return type.
    """
    if not callable(obj):
        raise TypeError(f"{obj} is not callable")
    signature = inspect.signature(obj)
    return_type = get_type_hints(obj).get("return", None)
    return {
        "name": obj.__name__,
        "parameters": {k: v.annotation for k, v in signature.parameters.items()},
        "return_type": return_type,
    }
