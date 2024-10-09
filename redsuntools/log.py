import logging
import sys
import coloredlogs
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

_logger: "Logger" = None  # Global logger instance

def setup_logger(component: str, log_file: str = "app.log", level: int = logging.INFO) -> "Logger":
    """
    Setup a single logger instance with two streams: stdout (with colored logs) and file.
    The format is dynamically set based on the provided component (e.g., Core, PluginA).
    
    Parameters
    ----------
    component : str
        Name of the component (e.g., Core, PluginA) to include in the log format.
    log_file : str
        Path to the log file.
    level : int
        Logging level (e.g., logging.INFO, logging.DEBUG).
    
    Returns
    -------
    Logger
        Configured logger instance.
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger("central_logger")
        _logger.setLevel(level)

        # Console Handler (with colored logs)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # File Handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Formatter with dynamic component name (e.g., Core, PluginA)
        log_format = f'[ %(asctime)s ][ {component} -> %(funcName)s ]: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        # Colored logs setup
        coloredlogs.install(
            level=level,
            logger=_logger,
            fmt=log_format,
            datefmt=date_format,
            stream=sys.stdout
        )

        # File formatter without coloredlogs (standard file logging)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)

        _logger.addHandler(console_handler)
        _logger.addHandler(file_handler)

    return _logger

def get_logger() -> "Logger":
    """
    Get the shared logger instance.

    Returns
    -------
    Logger
        Shared logger instance.
    """
    global _logger
    if _logger is None:
        raise RuntimeError("Logger has not been initialized. Call setup_logger first.")
    
    return _logger