"""This module is concerned with a rabbitmq connections
"""

import contextlib
from typing import Generator

import pika
from pika.adapters.blocking_connection import BlockingChannel

from .utils import get_logger

logger = get_logger(__name__)


@contextlib.contextmanager
def channel_manager(host: str) -> Generator[BlockingChannel, None, None]:
    """Context manager that provides a channel connection to a queue on rabbitmq"""

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.queue_declare(queue="files")

    logger.info("Backend listening to queue.")

    yield channel
    channel.cancel()
    channel.close()
    connection.close()
