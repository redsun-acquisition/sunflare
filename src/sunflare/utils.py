from typing import Any, Callable, TypeVar
from functools import partial, wraps
from bluesky.utils import MsgGenerator

T = TypeVar("T")


def make_plan(
    plan: Callable[..., MsgGenerator[T]], *args: Any, **kwargs: Any
) -> partial[MsgGenerator[T]]:
    """Define a plan with arguments.

    The decorator allows for plans to be partially applied with arguments,
    keeping the original metadata.
    """

    @wraps(plan)
    def wrapped_plan(*inner_args: Any, **inner_kwargs: Any) -> MsgGenerator[T]:
        return plan(*inner_args, **inner_kwargs)

    return partial(wrapped_plan, *args, **kwargs)
