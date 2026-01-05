"""This module is concerned with defining the Celery client that is used to send tasks to the broker queue."""

from collections.abc import Generator

from celery import Celery

from api.core.config import settings


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
        "tasks",
        broker=f"amqp://{settings.default_user}:{settings.default_pass}@{host}:5672/",
        backend="rpc://",
    )
    yield client
    client.close()
