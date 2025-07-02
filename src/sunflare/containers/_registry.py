from __future__ import annotations

import inspect
from collections.abc import Generator, Iterable, Mapping, Sequence, Set  # noqa: TC003
from typing import (
    Any,
    Callable,
    TypeGuard,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)
from weakref import WeakKeyDictionary

from bluesky.utils import Msg

from sunflare.controller import ControllerProtocol
from sunflare.model import ModelProtocol

PlanGenerator = Callable[..., Generator[Msg, Any, Any]]

#: Registry for storing model protocols
#: The dictionary maps the protocol owners to a set of `ModelProtocol` types.
protocol_registry: WeakKeyDictionary[ControllerProtocol, set[type[ModelProtocol]]] = (
    WeakKeyDictionary()
)

#: Registry for storing plan generators
#: The dictionary maps plan owners to plan names to their callable functions
plan_registry: WeakKeyDictionary[ControllerProtocol, dict[str, PlanGenerator]] = (
    WeakKeyDictionary()
)


def _is_model_protocol(proto: type) -> TypeGuard[type[ModelProtocol]]:
    """Type guard to check if a type implements ModelProtocol."""
    return ModelProtocol in proto.mro() or isinstance(proto, ModelProtocol)


def _check_protocol_in_generic(annotation: Any) -> bool:
    """
    Check if an annotation contains protocols, including in generic types.

    Returns
    -------
    bool
        True if a protocol is found, False otherwise.
    """
    # Check for generic types - use iterative approach instead of recursion
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is not None and args:
        # Check if it's a supported generic type
        if origin in (Sequence, Iterable, Mapping, Set):
            # Flatten all type arguments and check each one
            types_to_check = list(args)
            while types_to_check:
                arg = types_to_check.pop()

                # Use improved protocol check
                if isinstance(arg, type) and _is_model_protocol(arg):
                    return True

                # If it's a generic type, add its args to the list to check
                nested_origin = get_origin(arg)
                nested_args = get_args(arg)
                if nested_origin is not None and nested_args:
                    types_to_check.extend(nested_args)

    return False


def _extract_protocol_types_from_generic(
    annotation: Any, registered_protocols: set[type[ModelProtocol]]
) -> list[type]:
    """
    Extract all protocol types from a generic annotation and check if they're registered.

    Parameters
    ----------
    annotation : Any
        The type annotation to inspect.
    registered_protocols : set
        A set of registered protocol types to check against.

    Returns
    -------
        list[type]: List of unregistered protocol types found in the annotation
    """
    unregistered = []

    # Use improved protocol check for direct protocols
    if isinstance(annotation, type) and _is_model_protocol(annotation):
        if annotation not in registered_protocols:
            unregistered.append(annotation)
        return unregistered

    # Check for generic types - use iterative approach
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is not None and args:
        # Flatten all type arguments and check each one
        types_to_check = list(args)
        while types_to_check:
            arg = types_to_check.pop()

            # Use improved protocol check
            if isinstance(arg, type) and _is_model_protocol(arg):
                if arg not in registered_protocols:
                    unregistered.append(arg)
            else:
                # If it's a generic type, add its args to the list to check
                nested_origin = get_origin(arg)
                nested_args = get_args(arg)
                if nested_origin is not None and nested_args:
                    types_to_check.extend(nested_args)

    return unregistered


def _validate_plan_protocols(
    sig: inspect.Signature,
    type_hints: dict[str, Any],
    plan_name: str,
    owner: ControllerProtocol,
) -> None:
    """Validate that all protocols used in plan parameters are registered."""
    registered_protocols = protocol_registry.get(owner, set())

    for param_name, param in sig.parameters.items():
        # Get the resolved type from type_hints, fallback to annotation
        resolved_type = type_hints.get(param_name, param.annotation)

        # Check if it's a protocol (including generics)
        is_protocol = _check_protocol_in_generic(resolved_type)

        if is_protocol:
            # Extract all protocol types from the annotation (handles generics)
            unregistered_protocols = _extract_protocol_types_from_generic(
                resolved_type, registered_protocols
            )

            if unregistered_protocols:
                protocol_names = [p.__name__ for p in unregistered_protocols]
                raise TypeError(
                    f"Protocols {protocol_names} used in plan {plan_name} are not registered for owner {owner}"
                )


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
    for proto in protos:
        if not _is_model_protocol(proto):
            raise TypeError(f"Protocol {proto.__name__} must implement ModelProtocol")

    if owner not in protocol_registry:
        protocol_registry[owner] = set()
    protocol_registry[owner].update(protos)


@overload
def register_plans(
    owner: ControllerProtocol,
    plans: PlanGenerator,
) -> None: ...


@overload
def register_plans(
    owner: ControllerProtocol,
    plans: Iterable[PlanGenerator],
) -> None: ...


def register_plans(
    owner: ControllerProtocol,
    plans: PlanGenerator | Iterable[PlanGenerator],
) -> None:
    """Register one or multiple plan generators.

    Plans are expected to be callable objects that return a Bluesky message generator.
    Plan generators can require parameters, including protocols inherited from `ModelProtocol`;
    the requirement for using protocols in a plan is that they have to be registered first via
    the `register_protocols` function.

    Parameters
    ----------
    owner : ``ControllerProtocol``
        The owner of the plan.
    plans : ``PlanGenerator | Iterable[PlanGenerator]``
        The plan generator or generators to register.

    Raises
    ------
    TypeError
        If the owner does not implement `ControllerProtocol`,
        if the plans are not callable or if they do not return a `Generator[Msg, Any, Any]`,
        if the yield type of the generator is not `Msg`
        or a parameter using a protocol that is not registered is found.
    """
    if not isinstance(owner, ControllerProtocol):
        raise TypeError(f"Owner must implement ControllerProtocol, got {type(owner)}")

    # Convert input to a set to ensure uniqueness
    if callable(plans):
        obj_plans = {plans}
    else:
        obj_plans = set(plans)

    # Validate all plans before registering any
    plan_names: dict[PlanGenerator, str] = {}
    for plan in obj_plans:
        if not callable(plan):
            raise TypeError("Plans must be callable objects that return a Generator")

        try:
            if inspect.ismethod(plan) or inspect.isfunction(plan):
                if not inspect.isgeneratorfunction(plan):
                    raise TypeError(f"Plan {plan} must be a generator function")
                plan_name = plan.__qualname__
                type_hints = get_type_hints(plan)
            elif hasattr(plan, "__call__"):
                if not inspect.isgeneratorfunction(plan.__call__):
                    raise TypeError(
                        f"Plan {plan.__call__.__qualname__} must be a generator function"
                    )
                plan_name = plan.__call__.__qualname__.split(".")[-2]
                type_hints = get_type_hints(plan.__call__)
            else:
                raise TypeError(f"{plan} is not callable")
        except TypeError:
            raise

        plan_names[plan] = plan_name

        if "return" in type_hints:
            return_type = type_hints["return"]
            # Check if return type is a Generator that yields Msg
            origin = get_origin(return_type)
            if origin is not None:
                # Handle generic types like Generator[Msg, Any, Any]
                if origin is not Generator:
                    raise TypeError(
                        f"Plan {plan_name} must return a Generator, got {return_type}"
                    )
                # Check that it yields Msg objects
                args = get_args(return_type)
                if args and len(args) >= 1:
                    yield_type = args[0]  # First type arg is what the generator yields
                    if yield_type is not Msg:
                        raise TypeError(
                            f"Plan {plan_name} must return a Generator that yields Msg, got Generator[{yield_type}, ...]"
                        )
            else:
                # Check if it's at least a Generator (fallback)
                try:
                    if not issubclass(return_type, Generator):
                        raise TypeError(
                            f"Plan {plan_name} must return a Generator, got {return_type}"
                        )
                except TypeError:
                    # return_type is not a class, so can't use issubclass
                    raise TypeError(
                        f"Plan {plan_name} must return a Generator, got {return_type}"
                    )
        else:
            raise TypeError(f"Plan {plan_name} must have a return type annotation")

    try:
        _validate_plan_protocols(inspect.signature(plan), type_hints, plan_name, owner)
    except TypeError as e:
        raise TypeError(f"Plan {plan_name} has invalid protocol usage: {e}") from e

    # If all checks passed, register the plans
    if owner not in plan_registry:
        plan_registry[owner] = {}

    # Use string names as keys and functions as values
    for plan in obj_plans:
        plan_name = plan_names[plan]
        plan_registry[owner][plan_name] = plan


def get_protocols() -> dict[ControllerProtocol, set[type[ModelProtocol]]]:
    """Get the available protocols.

    Returns
    -------
    dict[ControllerProtocol, set[type[ModelProtocol]]]
        A mapping of controller protocols to their registered model protocols.
    """
    return dict(protocol_registry)


def get_plans() -> dict[ControllerProtocol, dict[str, PlanGenerator]]:
    """Get the available plans.

    Returns
    -------
    dict[ControllerProtocol, dict[str, PlanGenerator]]
        A mapping of controller protocols to their registered plan names and functions.
    """
    return dict(plan_registry)
