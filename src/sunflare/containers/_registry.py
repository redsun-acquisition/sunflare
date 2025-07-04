from __future__ import annotations

import inspect
from collections.abc import Generator, Iterable, Mapping, Sequence, Set  # noqa: TC003
from dataclasses import dataclass
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
from weakref import WeakKeyDictionary

from bluesky.utils import Msg

from sunflare.controller import ControllerProtocol
from sunflare.model import ModelProtocol

PlanGenerator = Callable[..., Generator[Msg, Any, Any]]


@dataclass(frozen=True)
class ParameterInfo:
    """Information about a single parameter in a plan signature."""

    annotation: type[Any]
    kind: inspect._ParameterKind
    default: Any
    origin: type[Any] | None

    def __hash__(self) -> int:
        return hash(
            (str(self.annotation), self.kind, str(self.default), str(self.origin))
        )

    @classmethod
    def from_parameter(
        cls, param: inspect.Parameter, resolved_type: type[Any]
    ) -> "ParameterInfo":
        """Create a ParameterInfo from an inspect.Parameter and resolved type.

        Parameters
        ----------
        param : inspect.Parameter
            The parameter to extract information from.
        resolved_type : type[Any]
            The resolved type annotation.

        Returns
        -------
        ParameterInfo
            A new ParameterInfo instance with the extracted information.
        """
        origin = get_origin(resolved_type)

        return cls(
            annotation=resolved_type,
            kind=param.kind,
            default=param.default if param.default != inspect.Parameter.empty else None,
            origin=origin,
        )


@dataclass(frozen=True)
class PlanSignature:
    """Holds information about a plan's signature."""

    parameters: dict[str, ParameterInfo]

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.parameters.items())))

    @classmethod
    def from_callable(cls, func: Callable[..., Any]) -> "PlanSignature":
        """Create a PlanSignature from a callable.

        Parameters
        ----------
        func : Callable[..., Any]
            The callable to extract signature information from.

        Returns
        -------
        PlanSignature
            A new PlanSignature instance with the extracted information.
        """
        if inspect.ismethod(func) or inspect.isfunction(func):
            # Use the function's signature directly
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
        elif hasattr(func, "__call__"):
            # Use the __call__ method's signature if it's a callable object
            sig = inspect.signature(func.__call__)
            type_hints = get_type_hints(func.__call__)
        else:
            raise TypeError(
                f"{func} is not callable or does not have a valid signature"
            )

        # Extract parameter information
        parameters = {}
        for param_name, param in sig.parameters.items():
            # Get the resolved type from type_hints, fallback to annotation
            resolved_type = type_hints.get(param_name, param.annotation)

            # Create ParameterInfo instance (no name field needed)
            param_info = ParameterInfo.from_parameter(param, resolved_type)
            parameters[param_name] = param_info

        return cls(
            parameters=parameters,
        )


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

#: Registry for storing plan signatures
#: The dictionary maps plan owners to plan names to their signatures
signatures: WeakKeyDictionary[ControllerProtocol, dict[str, PlanSignature]] = (
    WeakKeyDictionary()
)


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
                if isinstance(arg, type) and isinstance(arg, ModelProtocol):
                    return True

                # If it's a generic type, add its args to the list to check
                nested_origin = get_origin(arg)
                nested_args = get_args(arg)
                if nested_origin is not None and nested_args:
                    types_to_check.extend(nested_args)

    return False


def _ismodel(arg: type[Any]) -> TypeGuard[type[ModelProtocol]]:
    return isinstance(arg, ModelProtocol)


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
    if isinstance(annotation, type) and _ismodel(annotation):
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
            if isinstance(arg, type) and _ismodel(arg):
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
        if not isinstance(proto, ModelProtocol):
            raise TypeError(f"Protocol {proto.__name__} must implement ModelProtocol")

    protocol_registry.setdefault(owner, set())
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
        # preemptively check if the plan is a callable object
        func: Callable[..., Generator[Msg, Any, Any]]

        if inspect.ismethod(plan) or inspect.isfunction(plan):
            func = plan
            func_name = func.__qualname__
            type_hints = get_type_hints(func)
        elif hasattr(plan, "__call__"):
            func = plan.__call__
            func_name = plan.__call__.__qualname__.split(".")[-2]
            type_hints = get_type_hints(plan.__call__)
        else:
            raise TypeError("Plans must be callable objects that return a Generator")

        if not inspect.isgeneratorfunction(func):
            raise TypeError(f"Plan {func_name} must be a generator function")

        plan_names[func] = func_name

        if "return" in type_hints:
            return_type = type_hints["return"]
            # Check if return type is a Generator that yields Msg
            origin = get_origin(return_type)
            if origin:
                # Handle generic types like Generator[Msg, Any, Any]
                if origin is not Generator:
                    raise TypeError(
                        f"Plan {func_name} must return a Generator, got {return_type}"
                    )
                # Check that it yields Msg objects
                args = get_args(return_type)
                if args and len(args) >= 1:
                    yield_type = args[0]  # First type arg is what the generator yields
                    if yield_type is not Msg:
                        raise TypeError(
                            f"Plan {func_name} must return a Generator that yields Msg, got Generator[{yield_type}, ...]"
                        )
            else:
                raise TypeError(
                    f"Plan {func_name} must have a return type annotation that is a Generator"
                )
        else:
            raise TypeError(
                f"Plan {func_name} must have a return type annotation that is a Generator"
            )

        try:
            _validate_plan_protocols(
                inspect.signature(func), type_hints, func_name, owner
            )
        except TypeError as e:
            raise TypeError(f"Plan {func_name} has invalid protocol usage: {e}") from e

        plan_registry.setdefault(owner, {})
        plan_registry[owner][func_name] = func

        signatures.setdefault(owner, {})
        signatures[owner][func_name] = PlanSignature.from_callable(func)


def get_protocols() -> MappingProxyType[ControllerProtocol, set[type[ModelProtocol]]]:
    """Get the available protocols.

    Returns
    -------
    MappingProxyType[ControllerProtocol, set[type[ModelProtocol]]]
        Read-only mapping of controller protocols to their registered model protocols.
    """
    return MappingProxyType(protocol_registry)


def get_plans() -> MappingProxyType[ControllerProtocol, dict[str, PlanGenerator]]:
    """Get the available plans.

    Plans are mapped as:
    - owner (``ControllerProtocol``): The owner of the plans.
      - ``dict[str, PlanGenerator]``: A dictionary mapping plan names to their generator functions.

    Returns
    -------
    MappingProxyType[ControllerProtocol, dict[str, PlanGenerator]]
        Read-only mapping of controller protocols to their registered plan names and functions.
    """
    return MappingProxyType(plan_registry)


def get_signatures() -> MappingProxyType[ControllerProtocol, dict[str, PlanSignature]]:
    """Get the available plan signatures.

    Signatures are mapped as:
    - owner (``ControllerProtocol``): The owner of the plans.
      - ``dict[str, PlanSignature]``: A dictionary mapping plan names to their signatures.



    Returns
    -------
    MappingProxyType[ControllerProtocol, dict[str, PlanSignature]]
        Read-only mapping of controller protocols to their registered plan signatures.
    """
    return MappingProxyType(signatures)
