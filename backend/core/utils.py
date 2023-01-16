"""This module is concerned with logging.
"""

import logging
import sys


def get_logger(name: str = "backend") -> logging.Logger:
    """Define a standard logger for the project"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # set logger level
    logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    consoleHandler = logging.StreamHandler(sys.stdout)  # set streamhandler to stdout
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    return logger
