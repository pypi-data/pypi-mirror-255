# -=- encoding: utf-8 -=-
#
# Copyright (c) 2024 Deeper Insights. Subject to the MIT license.

"""
Tests for the logging.

Note that it's really difficult to test the logging as pytest nobbles the logger...
"""
import logging

from di_logging import configure_logging, get_logger


def test_logging():
    """Do some logging.  We ain't gonna see much though."""
    configure_logging()
    logger = get_logger(__name__)
    logger.info("Test message")
    logging.info("Python logger")
