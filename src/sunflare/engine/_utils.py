from typing import Optional, MutableMapping, Any
from bluesky.run_engine import RunEngine

# main engine instance is created outside of sunflare;
# either directly from RedSun during initialization or
# the user can create it manually
RE: Optional[RunEngine] = None


def create_main_engine(
    *, md: Optional[MutableMapping[str, Any]] = None, **kwargs: Any
) -> None:
    """Create a new, unique `RunEngine` instance.

    Parameters
    ----------
    md : MutableMapping[str, Any]
        Mutable mapping used to store global session metadata.
    **kwargs : Any
        Additional keyword arguments. See :class:`bluesky.run_engine.RunEngine` for more details.
    """
    global RE
    if md is None:
        md = dict()
    RE = RunEngine(md=md, **kwargs)  # type: ignore[no-untyped-call]


def get_main_engine() -> RunEngine:
    """Return the global `RunEngine` instance.

    Returns
    -------
    `RunEngine`
        The global `RunEngine` instance.
    """
    global RE
    if RE is None:
        raise RuntimeError("The main engine is not initialized.")
    return RE
