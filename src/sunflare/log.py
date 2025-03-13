from __future__ import annotations

import logging
import logging.config
from typing import ClassVar

__all__ = ["Loggable"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class ClassFormatter(logging.Formatter):
    """Custom formatter for logging messages with class name and user-defined ID."""

    STD_FORMAT = "[%(asctime)s][%(levelname)s]"

    def __init__(self, datefmt: str) -> None:
        super().__init__(datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        fmt = self.STD_FORMAT
        message = []
        message.append(record.getMessage())
        record.message = " ".join(message)
        record.asctime = self.formatTime(record, self.datefmt)
        if "clsname" in record.__dict__:
            fmt += "[%(clsname)s"
            if "uid" in record.__dict__ and len(record.__dict__["uid"]) > 0:
                fmt += " -> %(uid)s"
            fmt += "]"
        fmt += " %(message)s"
        if record.levelno != logging.INFO:
            fmt += " (%(filename)s:%(lineno)d)"
        formatted = fmt % record.__dict__
        return formatted


class InfoFilter(logging.Filter):
    def __init__(self, name: str = "") -> None:
        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.INFO


class DebugFilter(logging.Filter):
    def __init__(self, name: str = "") -> None:
        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.INFO


config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"()": lambda: ClassFormatter(datefmt="%d-%m-%y|%H:%M:%S")}
    },
    "filters": {
        "info_filter": {"()": InfoFilter},  # Allows only INFO
        "debug_filter": {"()": DebugFilter},  # Excludes INFO
    },
    "handlers": {
        "info": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
            "filters": ["info_filter"],
        },
        "debug": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
            "filters": ["debug_filter"],
        },
    },
    "loggers": {
        "redsun": {"level": "DEBUG", "propagate": True, "handlers": ["info", "debug"]}
    },
}

# Set configuration
logging.config.dictConfig(config)

# base logger for the session
logger = logging.getLogger("redsun")


class Loggable:
    """
    Mixin class to extend log records with the class name and the user defined ID.

    Models and controllers can inherit from this class to have a consistent log format.

    All methods allow to forward extra arguments to the logger calls as documented in the `logging` module.
    """

    logger: ClassVar[logging.Logger] = logging.getLogger("redsun")

    def _extend(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Enrich kwargs with class name and user-defined ID.

        :meta-private:
        """
        kwargs["extra"] = {
            **kwargs.get("extra", {}),
            "clsname": self.__clsname__,
            "uid": self.name,
        }
        return kwargs

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an info message in the core logger.

        Parameters
        ----------
        msg : ``str``
            String to log.
        *args : ``Any``
            Additional positional arguments for ``logging.Logger.info``.
        **kwargs : ``Any``
            Additional keyword arguments for ``logging.Logger.info``.
        """
        self._extend(kwargs)
        logger.info(msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a debug message in the core logger.

        Parameters
        ----------
        msg : ``str``
            String to log.
        *args : ``Any``
            Additional positional arguments for ``logging.Logger.debug``.
        **kwargs : ``Any``
            Additional keyword arguments for ``logging.Logger.debug``.
        """
        self._extend(kwargs)
        logger.debug(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a warning message in the core logger.

        Parameters
        ----------
        msg : ``str``
            String to log.
        *args : ``Any``
            Additional positional arguments for ``logging.Logger.warning``.
        **kwargs : ``Any``
            Additional keyword arguments for ``logging.Logger.warning``.
        """
        self._extend(kwargs)
        logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an error. message in the core logger.

        Parameters
        ----------
        msg : ``str``
            String to log.
        *args : ``Any``
            Additional positional arguments for ``logging.Logger.error``.
        **kwargs : ``Any``
            Additional keyword arguments for ``logging.Logger.error``.
        """
        self._extend(kwargs)
        logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a critical message in the core logger.

        Parameters
        ----------
        msg : ``str``
            String to log.
        *args : ``Any``
            Additional positional arguments for ``logging.Logger.critical``.
        **kwargs : ``Any``
            Additional keyword arguments for ``logging.Logger.critical``.
        """
        self._extend(kwargs)
        logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an exception message in the core logger.

        Parameters
        ----------
        msg : ``str``
            String to log.
        *args : ``Any``
            Additional positional arguments for ``logging.Logger.exception``.
        **kwargs : ``Any``
            Additional keyword arguments for ``logging.Logger.exception``.
        """
        self._extend(kwargs)
        logger.exception(msg, *args, **kwargs)

    @property
    def __clsname__(self) -> str:
        """
        Class name.

        :meta-private:
        """
        # Private property, should not be
        # accessed by the user
        return self.__class__.__name__

    @property
    def name(self) -> str:
        """Class instance unique identifier.

        This property should be implemented by
        model classes by default.

        :meta-private:
        """
        return str()
