import logging
import logging.handlers
from logging import CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET
from platform import system
from typing import Optional
import os

levels = {
    "CRITICAL": CRITICAL,
    "FATAL": FATAL,
    "ERROR": ERROR,
    "WARN": WARNING,
    "WARNING": WARNING,
    "INFO": INFO,
    "DEBUG": DEBUG,
    "NOTSET": NOTSET,
}


def get_logger(name: str, *, min_level: Optional[int] = None) -> logging.Logger:
    level = INFO
    env_string = os.environ.get("LOG_LEVEL")
    if env_string is not None:
        if env_string not in levels:
            raise ValueError(f"Invalid log level as LOG_LEVEL: {env_string}")
        level = levels[env_string]
    if min_level is not None and min_level > level:
        level = min_level
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if system() == "FreeBSD":
        logger.addHandler(logging.handlers.SysLogHandler(address="/var/run/log"))
    return logger
