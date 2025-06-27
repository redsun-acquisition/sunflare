from __future__ import annotations

import collections.abc
import inspect
from collections.abc import Iterable  # noqa: TC003
from dataclasses import dataclass
from functools import cached_property
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    TypeGuard,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from bluesky.utils import MsgGenerator

from sunflare.controller import ControllerProtocol
from sunflare.model import ModelProtocol


def _get_callable_for_inspection(
    func: Callable[..., MsgGenerator],
) -> Callable[..., MsgGenerator]:
    """Get the actual callable object for signature inspection."""
    if isinstance(func, (staticmethod, classmethod)):
        return func.__func__
    elif (
        hasattr(func, "__call__")
        and hasattr(func, "__class__")
        and not inspect.isfunction(func)
        and not inspect.ismethod(func)
    ):
        # For callable objects, inspect the __call__ method
        return func.__call__
    return func


def _get_plan_name_and_type(func: Callable[..., MsgGenerator]) -> str:
    """
    Get the appropriate plan name for different callable objects.

    Returns
    -------
    str
        The name of the plan function, including class name for methods.
        If the function implements ``__call__``, it will return the class name.
    """
    if inspect.isfunction(func):
        return func.__name__
    elif inspect.ismethod(func):
        # Bound instance method
        return f"{func.__self__.__class__.__name__}.{func.__name__}"
    elif isinstance(func, staticmethod):
        # Static method - get the underlying function
        underlying_func = func.__func__
        # Get the class name from the qualified name if available
        if (
            hasattr(underlying_func, "__qualname__")
            and "." in underlying_func.__qualname__
        ):
            class_name = underlying_func.__qualname__.split(".")[-2]
            return f"{class_name}.{underlying_func.__name__}"
        return underlying_func.__name__
    elif isinstance(func, classmethod):
        # Class method - get the underlying function
        underlying_func = func.__func__
        # Get the class name from the qualified name if available
        if (
            hasattr(underlying_func, "__qualname__")
            and "." in underlying_func.__qualname__
        ):
            class_name = underlying_func.__qualname__.split(".")[-2]
            return f"{class_name}.{underlying_func.__name__}"
        return underlying_func.__name__
    elif hasattr(func, "__call__") and hasattr(func, "__class__"):
        # Callable object with __call__ method - use class name with __call__
        class_name = func.__class__.__name__
        return f"{class_name}"
    else:
        # Fallback for other callable objects
        return getattr(func, "__name__", str(func))


@dataclass(frozen=True)
class ParameterInfo:
    """Information about a function parameter.

    Parameters
    ----------
    name : str
        The name of the parameter.
    annotation : Any
        The type annotation of the parameter.
    default : Any
        The default value of the parameter, if any.
    kind : inspect.Parameter
        The kind of the parameter (e.g., positional, keyword, etc.).
    is_protocol : bool
        Whether the parameter is a protocol type.
    is_generic_protocol : bool
        Whether the parameter is a generic protocol type.
    generic_args : tuple[Any, ...], optional
        Type arguments for generics, if applicable.
        If the parameter is a generic protocol, this will contain the type arguments.
    """

    name: str
    annotation: Any
    default: Any
    kind: inspect.Parameter
    is_protocol: bool
    is_generic_protocol: bool  # New field for generic protocol types
    generic_args: tuple[Any, ...] | None = None  # Type arguments for generics


@dataclass(frozen=True)
class PlanSignature:
    """A dataclass to hold the complete signature of a plan.

    Parameters
    ----------
    name : str
        The name of the plan function.
    parameters : MappingProxyType[str, ParameterInfo]
        An immutable mapping of parameter names to their information.
    """

    name: str
    parameters: MappingProxyType[str, ParameterInfo]  # Immutable dict for hashability

    @cached_property
    def _hash(self) -> int:
        """Cached hash computation for performance."""
        params_tuple = tuple(sorted(self.parameters.items()))
        return hash((self.name, params_tuple))

    def __hash__(self) -> int:
        """Hash implementation using cached property."""
        return self._hash

    @classmethod
    def from_function(cls, func: Callable[..., MsgGenerator]) -> "PlanSignature":
        """Create a PlanSignature from a function, method, or other callable."""
        # Get the appropriate name and the actual callable for inspection
        plan_name = _get_plan_name_and_type(func)
        inspectable_func = _get_callable_for_inspection(func)

        sig = inspect.signature(inspectable_func)
        type_hints = get_type_hints(inspectable_func)

        parameters = {}
        for param_name, param in sig.parameters.items():
            # Get the resolved type from type_hints, fallback to annotation
            resolved_type = type_hints.get(param_name, param.annotation)

            # Check if it's a protocol (including generics)
            is_protocol, is_generic_protocol, generic_args = _check_protocol_in_generic(
                resolved_type
            )

            parameters[param_name] = ParameterInfo(
                name=param_name,
                annotation=resolved_type,
                default=param.default
                if param.default != inspect.Parameter.empty
                else None,
                kind=param.kind,
                is_protocol=is_protocol,
                is_generic_protocol=is_generic_protocol,
                generic_args=generic_args,
            )

        return cls(
            name=plan_name,
            parameters=MappingProxyType(parameters),  # Make it immutable
        )


#: Registry for storing model protocols
#: The dictionary maps the protocol owners to a set of `ModelProtocol` types.
protocol_registry: dict[str, set[type[ModelProtocol]]] = {}

#: Registry for storing plan generators with their detailed signatures
#: The dictionary maps plan owners to PlanSignature objects to their callable functions
plan_registry: dict[str, dict[PlanSignature, Callable[..., MsgGenerator]]] = {}


def _is_model_protocol(proto: type) -> TypeGuard[type[ModelProtocol]]:
    """Type guard to check if a type implements ModelProtocol."""
    return ModelProtocol in proto.mro()


def _check_protocol_in_generic(
    annotation: Any,
) -> tuple[bool, bool, tuple[Any, ...] | None]:
    """
    Check if an annotation contains protocols, including in generic types.

    Returns
    -------
        tuple[bool, bool, tuple[Any, ...] | None]
        A tuple where:
        - The first element is True if a protocol is found, False otherwise.
        - The second element is True if the annotation is a generic type, False otherwise.
        - The third element is the type arguments if the annotation is a generic type, None otherwise
    """
    # Direct protocol check
    if isinstance(annotation, type) and ModelProtocol in annotation.mro():
        return True, False, None

    # Check for generic types
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is not None and args:
        # Check if it's a supported generic type
        if origin in (
            collections.abc.Sequence,
            collections.abc.Iterable,
            collections.abc.Mapping,
            collections.abc.Set,
            list,
            tuple,
            set,
            dict,
        ):
            # Check if any of the type arguments are protocols
            for arg in args:
                if isinstance(arg, type) and ModelProtocol in arg.mro():
                    return True, True, args

                # Recursively check nested generics
                nested_is_protocol, _, _ = _check_protocol_in_generic(arg)
                if nested_is_protocol:
                    return True, True, args

    return False, False, None


def _extract_protocol_types_from_generic(
    annotation: Any, registered_protocols: set
) -> list[type]:
    """
    Extract all protocol types from a generic annotation and check if they're registered.

    Returns
    -------
        list[type]: List of unregistered protocol types found in the annotation
    """
    unregistered = []

    # Direct protocol check
    if isinstance(annotation, type) and ModelProtocol in annotation.mro():
        if annotation not in registered_protocols:
            unregistered.append(annotation)
        return unregistered

    # Check for generic types
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is not None and args:
        for arg in args:
            if isinstance(arg, type) and ModelProtocol in arg.mro():
                if arg not in registered_protocols:
                    unregistered.append(arg)
            else:
                # Recursively check nested generics
                nested_unregistered = _extract_protocol_types_from_generic(
                    arg, registered_protocols
                )
                unregistered.extend(nested_unregistered)

    return unregistered


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


@overload
def register_plans(
    owner: ControllerProtocol,
    plans: Callable[..., MsgGenerator],
) -> None: ...
@overload
def register_plans(
    owner: ControllerProtocol,
    plans: Iterable[Callable[..., MsgGenerator]],
) -> None: ...
def register_plans(
    owner: ControllerProtocol,
    plans: Callable[..., MsgGenerator] | Iterable[Callable[..., MsgGenerator]],
) -> None:
    """Register one or multiple plan generators.

    Plans are expected to be callable objects that return a Bluesky message generator.
    Plan generators can require parameters, including protocols inherited from `ModelProtocol`;
    the requirement for using procotols in a plan is that they have to be registered first via
    the `register_protocols` function.

    Parameters
    ----------
    owner : ``ControllerProtocol``
        The owner of the plan.
    plans : ``Callable[..., MsgGenerator] | Iterable[Callable[..., MsgGenerator]]``
        The plan generator or generators to register.

    Raises
    ------
    TypeError
        If the owner does not implement `ControllerProtocol`,
        if the plans are not callable or if they do not return a `MsgGenerator`.
    """
    if not isinstance(owner, ControllerProtocol):
        raise TypeError(f"Owner must implement ControllerProtocol, got {type(owner)}")
    owner_name = owner.__class__.__name__

    # Convert input to a set to ensure uniqueness
    if isinstance(plans, Callable):
        obj_plans = {plans}
    else:
        obj_plans = set(plans)

    # Validate all plans before registering any
    plan_signatures = {}
    for plan in obj_plans:
        if not callable(plan):
            raise TypeError("Plans must be callable objects that return a MsgGenerator")

        # Get the actual function for inspection
        inspectable_func = PlanSignature._get_callable_for_inspection(plan)

        if not inspect.isgeneratorfunction(inspectable_func):
            raise TypeError(f"Plan {plan} must be a generator function")

        # Create the plan signature with all type information preserved
        plan_sig = PlanSignature.from_function(plan)

        # Validate return type using the inspectable function
        type_hints = get_type_hints(inspectable_func)
        if "return" not in type_hints or type_hints["return"] is not MsgGenerator:
            raise TypeError(f"Plan {plan} must return a MsgGenerator")

        # Check if the plan requires any protocols (including in generics)
        for param_info in plan_sig.parameters.values():
            if param_info.is_protocol:
                # Get registered protocols for this owner
                registered_protocols = protocol_registry.get(owner_name, set())

                # Extract all protocol types from the annotation (handles generics)
                unregistered_protocols = _extract_protocol_types_from_generic(
                    param_info.annotation, registered_protocols
                )

                if unregistered_protocols:
                    protocol_names = [p.__name__ for p in unregistered_protocols]
                    raise TypeError(
                        f"Protocols {protocol_names} used in plan {plan_sig.name} are not registered for owner {owner_name}"
                    )

        plan_signatures[plan_sig.name] = plan_sig

    # If all checks passed, register the plans with their complete signatures
    if owner_name not in plan_registry:
        plan_registry[owner_name] = {}

    # Use PlanSignature objects as keys and functions as values
    for plan in obj_plans:
        plan_sig = plan_signatures[PlanSignature._get_plan_name_and_type(plan)]
        plan_registry[owner_name][plan_sig] = plan
