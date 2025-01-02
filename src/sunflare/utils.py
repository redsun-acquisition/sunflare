from functools import partial
from typing import Any, Callable

from bluesky.utils import MsgGenerator


def partial_plan(
    plan: Callable[..., MsgGenerator[Any]], *args: Any, **kwargs: Any
) -> partial[MsgGenerator[Any]]:
    """Define a partial plan with arguments.

    The decorator allows for plans to be partially applied with arguments,
    keeping the original metadata.

    Parameters
    ----------
    plan : Callable[..., MsgGenerator[Any]]
        Plan to be partially applied.
    *args : Any
        Arguments to be partially applied.
    **kwargs : Any
        Keyword arguments to be partially applied.

    Returns
    -------
    partial[MsgGenerator[Any]]
        Partially applied plan.
    """
    p = partial(plan, *args, **kwargs)
    setattr(p, "__name__", plan.__name__)
    setattr(p, "__doc__", plan.__doc__)
    setattr(p, "__annotations__", plan.__annotations__)
    return p
