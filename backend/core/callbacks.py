"""This module is concerned with functions triggered when new messages hit the rabbitmq server.
"""

import json

from .utils import get_logger

logger = get_logger(__name__)


def callback(body: dict) -> None:
    """Function that is called whenever a correctly formatted message is received"""
    logger.info(f"callback Received message : {body = }")
    return


def unsupported_callback(body) -> None:
    """Function that is called whenever the received message is unsupported"""
    logger.info(f"unsupported_callback: {body = }")
    return


def callback_handler(body) -> None:
    """Function that decides which callback function is called for a received message"""
    try:
        body = json.loads(body)
    except TypeError:
        pass

    try:
        content_type = body.get("content_type")
    except AttributeError:
        unsupported_callback(body)
        return

    if content_type == "text/plain":
        callback(body)
    else:
        unsupported_callback(body)
    return
