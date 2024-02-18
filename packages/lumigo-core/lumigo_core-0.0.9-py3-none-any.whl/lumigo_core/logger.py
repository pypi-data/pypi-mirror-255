import logging
import os
from typing import Dict

LOG_FORMAT = "#LUMIGO# - %(levelname)s - %(asctime)s - %(message)s"

_logger: Dict[str, logging.Logger] = {}


def is_debug() -> bool:
    return os.environ.get("LUMIGO_DEBUG", "").lower() == "true"


def get_logger(logger_name: str = "lumigo") -> logging.Logger:
    """
    This function returns lumigo's logger.
    The logger streams the logs to the stderr in format the explicitly say that those are lumigo's logs.

    This logger is off by default.
    Add the environment variable `LUMIGO_DEBUG=true` to activate it.
    """
    global _logger
    if logger_name not in _logger:
        _logger[logger_name] = logging.getLogger(logger_name)
        _logger[logger_name].propagate = False
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        if is_debug():
            _logger[logger_name].setLevel(logging.DEBUG)
        else:
            _logger[logger_name].setLevel(logging.CRITICAL)
        _logger[logger_name].addHandler(handler)
    return _logger[logger_name]
