from loguru import logger


def configure_logger(path: str, level="INFO", service="Default service",**kwargs):
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
    logger.add(sink=path, level=level, rotation="1 week", compression="zip", format="{time} - {level} - {message}")
    
    logger.add(sink="stdout", level=level, format="{time} - {level} - {message}")
    logger = logger.bind(service=service)
