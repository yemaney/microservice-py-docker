import json
from unittest import mock

from backend.core.callbacks import callback_handler
from backend.main import main


@mock.patch("backend.main.core.callback_handler")
def test_callback_handler_called(mock_callback_handler, channel):
    message_sent = {"filename": "myfile.txt", "content_type": "text/plain"}
    message_received = json.dumps(message_sent).encode("utf-8")

    channel.basic_publish(exchange="", routing_key="files_test", body=json.dumps(message_sent))
    main("localhost", "files_test", early_exit=True)

    mock_callback_handler.assert_called()
    mock_callback_handler.assert_called_with(message_received)


@mock.patch("backend.core.callbacks.callback")
def test_callback_called(mock_callback):
    message = {"filename": "myfile.txt", "content_type": "text/plain"}
    callback_handler(message)

    mock_callback.assert_called()
    mock_callback.assert_called_with(message)


@mock.patch("backend.core.callbacks.unsupported_callback")
def test_unsupported_callback_called(mock_unsupported_callback):
    message = {"filename": "myfile.txt", "content_type": "image/gif"}
    callback_handler(message)

    mock_unsupported_callback.assert_called()
    mock_unsupported_callback.assert_called_with(message)
