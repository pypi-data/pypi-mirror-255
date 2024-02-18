# -=- encoding: utf-8 -=-
#
# Copyright (c) 2024 Deeper Insights. Subject to the MIT license.

"""Factory methods for creating and configuring loggers."""
import logging
import os
import sys
from typing import Optional

from loguru import logger

LOGGER_FORMAT = (
    "<level>{level: <8}</level> "
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "- <level>{message}</level> "
)


class _InterceptHandler(logging.Handler):  # pragma: nocover
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while (
            frame is not None
            and frame.f_code is not None
            and frame.f_code.co_filename == logging.__file__
        ):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def get_logger(name: str):  # pylint: disable=unused-argument
    """
    Retrieve a logger for a specific module (name).

    Note that for a loguru logger the name is ignored as module specific handling is done
    when log records are created.

    Usage:

    mylib/__init__.py
        from di_logging import get_logger

        logger = get_logger(__name__)

    mylib/other_file.py
        from my_lib import logger

        logger.info("My log message")

    :param name: the name for the logger
    :type name: str
    :return: the logger
    """
    return logger


def configure_logging(file_path: Optional[str] = None):
    """
    Configure the logging for a system/application.

    This method needs to be called in the entry point of an application.
    It will configure the loguru logger and also intercept python logging and redirect
    it to the loguru logger.

    Usage:
    main.py
        from di_logging import configure_logging

        if __name__ == "__main__":
            configure_logging()
            run_my_awesome_app()
    """
    level = os.environ.get("LOG_LEVEL", "DEBUG")
    logger.remove()
    logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        level=level.upper(),
        format=LOGGER_FORMAT,
    )
    if file_path:
        logger.add(
            file_path,
            rotation="500 MB",
            compression="zip",
            level=level.upper(),
            backtrace=True,
            format=LOGGER_FORMAT,
        )

    # add an intercept handler to the standard python logging so we get all logs to our logger
    logging.basicConfig(handlers=[_InterceptHandler()], level=0)
