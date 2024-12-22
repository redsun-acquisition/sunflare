# noqa: D104
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sunflare")
except PackageNotFoundError:
    __version__ = "unknown"
