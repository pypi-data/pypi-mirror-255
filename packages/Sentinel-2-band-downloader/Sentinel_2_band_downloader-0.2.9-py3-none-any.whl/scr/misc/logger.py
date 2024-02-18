import os
from loguru import logger


def configure_logger(level="INFO",**kwargs):
    """
    Configure a logger with two sinks.

    Parameters:
    -----------
    path: str
        The path to the log file.
    level: str
        The logging level (default is "INFO").
    **kwargs:
        Additional keyword arguments for logger configuration.
    """
    logger.add(sink="stdout", level=level, format="{time} - {level} - {message}")

