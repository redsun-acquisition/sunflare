# noqa: D104
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sunflare")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
