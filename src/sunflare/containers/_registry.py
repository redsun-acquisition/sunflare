from __future__ import annotations

import inspect
from collections.abc import Generator, Iterable, Mapping, Sequence, Set  # noqa: TC003
from typing import (
    Any,
    Callable,
    TypeGuard,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)
from weakref import WeakKeyDictionary

from bluesky.utils import Msg

from sunflare.controller import ControllerProtocol
from sunflare.model import ModelProtocol


def ismethoddescriptor(
    cls: type[Any],
    method_name: str,
    descriptor_type: type[staticmethod[Any, Any] | classmethod[Any, Any, Any]],
) -> bool:
    """Check if a method is of a specific descriptor type.

    Parameters
    ----------
    obj : type[Any]
        The class to check for the method.
    method_name : str
        The name of the method to check.
    descriptor_type : type[staticmethod[Any, Any] | classmethod[Any, Any, Any]]
        The type of descriptor to check against, either `staticmethod` or `classmethod`.

    Returns
    -------
    bool
        True if the method is a descriptor of the specified type, False otherwise.
    """
    is_type = method_name in cls.__dict__ and isinstance(
        cls.__dict__[method_name], descriptor_type
    )
    return is_type


def _get_plan_name(func: Callable[..., Generator[Msg, Any, Any]]) -> str:
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

    if inspect.ismethod(func):
        # Bound instance method - check if it's actually a static/class method
        obj = func.__self__
        cls = func.__class__
        method_name = func.__name__

        if ismethoddescriptor(cls, method_name, staticmethod):
            # It's a static method accessed through an instance
            static_method = cast("staticmethod[Any, Any]", getattr(cls, method_name))
            underlying_func = static_method.__func__
            if (
                hasattr(underlying_func, "__qualname__")
                and "." in underlying_func.__qualname__
            ):
                class_name = underlying_func.__qualname__.split(".")[-2]
                return f"{class_name}.{underlying_func.__name__}"
            return str(underlying_func.__name__)

        if ismethoddescriptor(cls, method_name, classmethod):
            # It's a class method
            class_method = cast("classmethod[Any, Any, Any]", getattr(cls, method_name))
            underlying_func = class_method.__func__
            if (
                hasattr(underlying_func, "__qualname__")
                and "." in underlying_func.__qualname__
            ):
                class_name = underlying_func.__qualname__.split(".")[-2]
                return f"{class_name}.{underlying_func.__name__}"
            return str(underlying_func.__name__)

        # Regular bound instance method
        return f"{obj.__class__.__name__}.{method_name}"

    if hasattr(func, "__call__") and hasattr(func, "__class__"):
        # Callable object with __call__ method - check if __call__ is static/class method
        class_obj = func.__class__
        if "__call__" in class_obj.__dict__:
            call_descriptor = class_obj.__dict__["__call__"]
            if isinstance(call_descriptor, staticmethod):
                call_underlying_func = call_descriptor.__func__
                return f"{class_obj.__name__}.{call_underlying_func.__name__}"
            if isinstance(call_descriptor, classmethod):
                call_underlying_func = call_descriptor.__func__
                return f"{class_obj.__name__}.{call_underlying_func.__name__}"
        # Regular callable object
        return class_obj.__name__

    # Fallback for other callable objects
    name_attr = getattr(func, "__name__", None)
    return str(name_attr) if name_attr is not None else str(func)


def _get_callable_for_inspection(
    func: type[Any] | Callable[..., Generator[Msg, Any, Any]],
) -> Callable[..., Generator[Msg, Any, Any]]:
    """Get the actual callable object for signature inspection."""
    if inspect.ismethod(func):
        # For bound methods, check if the underlying method is static/class method
        cls = func.__self__
        method_name = func.__name__

        if ismethoddescriptor(cls, method_name, staticmethod):
            static_method = cast("staticmethod[Any, Any]", getattr(cls, method_name))
            return cast(
                "Callable[..., Generator[Msg, Any, Any]]", static_method.__func__
            )
        if ismethoddescriptor(cls, method_name, classmethod):
            class_method = cast("classmethod[Any, Any, Any]", getattr(cls, method_name))
            return cast(
                "Callable[..., Generator[Msg, Any, Any]]", class_method.__func__
            )
        # Regular bound instance method
        return func

    if (
        hasattr(func, "__call__")
        and hasattr(func, "__class__")
        and not inspect.isfunction(func)
    ):
        # For callable objects, inspect the __call__ method
        return cast("Callable[..., Generator[Msg, Any, Any]]", func.__call__)

    return func


#: Registry for storing model protocols
#: The dictionary maps the protocol owners to a set of `ModelProtocol` types.
protocol_registry: WeakKeyDictionary[ControllerProtocol, set[type[ModelProtocol]]] = (
    WeakKeyDictionary()
)

#: Registry for storing plan generators
#: The dictionary maps plan owners to plan names to their callable functions
plan_registry: WeakKeyDictionary[
    ControllerProtocol, dict[str, Callable[..., Generator[Msg, Any, Any]]]
] = WeakKeyDictionary()


def _is_model_protocol(proto: type) -> TypeGuard[type[ModelProtocol]]:
    """Type guard to check if a type implements ModelProtocol."""
    return ModelProtocol in proto.mro()


def _check_protocol_in_generic(annotation: Any) -> bool:
    """
    Check if an annotation contains protocols, including in generic types.

    Returns
    -------
    bool
        True if a protocol is found, False otherwise.
    """
    # Direct protocol check
    if isinstance(annotation, type) and ModelProtocol in annotation.mro():
        return True

    # Check for generic types - use iterative approach instead of recursion
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is not None and args:
        # Check if it's a supported generic type
        if origin in (
            Sequence,
            Iterable,
            Mapping,
            Set,
            list,
            tuple,
            set,
            dict,
        ):
            # Flatten all type arguments and check each one
            types_to_check = list(args)
            while types_to_check:
                arg = types_to_check.pop()

                # Direct protocol check
                if isinstance(arg, type) and ModelProtocol in arg.mro():
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

    # Direct protocol check
    if isinstance(annotation, type) and ModelProtocol in annotation.mro():
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

            # Direct protocol check
            if isinstance(arg, type) and ModelProtocol in arg.mro():
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
    plan: Callable[..., Generator[Msg, Any, Any]],
    plan_name: str,
    owner: ControllerProtocol,
) -> None:
    """Validate that all protocols used in plan parameters are registered."""
    inspectable_func = _get_callable_for_inspection(plan)
    sig = inspect.signature(inspectable_func)
    type_hints = get_type_hints(inspectable_func)

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
    if not all(_is_model_protocol(proto) for proto in protos):
        raise TypeError("All protocols must be subclasses of ModelProtocol")

    if owner not in protocol_registry:
        protocol_registry[owner] = set()
    protocol_registry[owner].update(protos)


@overload
def register_plans(
    owner: ControllerProtocol,
    plans: Callable[..., Generator[Msg, Any, Any]],
) -> None: ...


@overload
def register_plans(
    owner: ControllerProtocol,
    plans: Iterable[Callable[..., Generator[Msg, Any, Any]]],
) -> None: ...


def register_plans(
    owner: ControllerProtocol,
    plans: Callable[..., Generator[Msg, Any, Any]]
    | Iterable[Callable[..., Generator[Msg, Any, Any]]],
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
    plans : ``Callable[..., Generator[Msg, Any, Any]] | Iterable[Callable[..., Generator[Msg, Any, Any]]]``
        The plan generator or generators to register.

    Raises
    ------
    TypeError
        If the owner does not implement `ControllerProtocol`,
        if the plans are not callable or if they do not return a `Generator[Msg, Any, Any]`.
    """
    if not isinstance(owner, ControllerProtocol):
        raise TypeError(f"Owner must implement ControllerProtocol, got {type(owner)}")

    # Convert input to a set to ensure uniqueness
    if callable(plans):
        obj_plans = {plans}
    else:
        obj_plans = set(plans)

    # Validate all plans before registering any
    plan_names: dict[Callable[..., Generator[Msg, Any, Any]], str] = {}
    for plan in obj_plans:
        if not callable(plan):
            raise TypeError("Plans must be callable objects that return a Generator")

        # Get the actual function for inspection
        inspectable_func = _get_callable_for_inspection(plan)

        if not inspect.isgeneratorfunction(inspectable_func):
            raise TypeError(f"Plan {plan} must be a generator function")

        # Get the plan name
        plan_name = _get_plan_name(plan)
        plan_names[plan] = plan_name

        # Validate return type using the inspectable function
        type_hints = get_type_hints(inspectable_func)
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

        # Validate protocol usage
        _validate_plan_protocols(plan, plan_name, owner)

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


def get_plans() -> dict[
    ControllerProtocol, dict[str, Callable[..., Generator[Msg, Any, Any]]]
]:
    """Get the available plans.

    Returns
    -------
    dict[ControllerProtocol, dict[str, Callable[..., Generator[Msg, Any, Any]]]]
        A mapping of controller protocols to their registered plan names and functions.
    """
    return dict(plan_registry)
