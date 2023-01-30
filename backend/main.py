"""Main entry point for the backend application.
"""

from . import core


def main(
    host: str = "rabbitmq",
    queue: str = "files",
    time_out: int = 5,
    early_exit: bool = False,
):
    """Handles starting the channel and calling the callback_handler function whenever a message is received"""
    with core.channel_manager(host) as channel:
        for method_frame, _, body in channel.consume(queue, inactivity_timeout=time_out):
            if method_frame:

                core.callback_handler(body)

                # Acknowledge the message
                channel.basic_ack(method_frame.delivery_tag)

                if early_exit:
                    break


if __name__ == "__main__":
    main()
