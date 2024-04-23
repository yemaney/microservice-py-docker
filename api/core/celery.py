"""This module is concerned with defining the Celery client that is used to send tasks to the broker queue."""

from typing import Generator

from celery import Celery


def get_celery_client(host: str = "rabbitmq") -> Generator[Celery, None, None]:
    """
    get_celery_client creates a celery app that will be used to connect to the task queue

    Parameters
    ----------
    host : str, optional
        host of the rabbitmq broker used for the celery task queue, by default "rabbitmq"

    Yields
    ------
    Celery
        celery app used to send tasks to the celery task queue
    """
    client = Celery(
        "tasks", broker=f"amqp://guest:guest@{host}:5672/", backend="rpc://"
    )
    yield client
    client.close()
