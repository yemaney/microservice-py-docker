"""This module is concerned with rabbitmq connection."""

import json
from typing import AsyncGenerator, Awaitable, Callable

import aio_pika


async def get_publisher(
    queue: str = "files",
) -> AsyncGenerator[Callable[[dict], Awaitable[None]], None]:
    async def publish_message(message: dict) -> None:
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()), routing_key=queue
        )

    connection = await aio_pika.connect_robust()
    channel = await connection.channel()

    await channel.declare_queue(queue)

    yield publish_message

    await connection.close()
