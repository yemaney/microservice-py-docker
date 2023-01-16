from typing import Generator

import pika
from pika.adapters.blocking_connection import BlockingChannel


def get_queue_channel() -> Generator[BlockingChannel, None, None]:

    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()

    channel.queue_declare(queue="files")
    yield channel
    connection.close()
