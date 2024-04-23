import time

from celery import Celery

app = Celery("tasks", broker="amqp://guest:guest@rabbitmq:5672", backend="rpc://")


@app.task(name="process_file")
def process_file(user_id: int, filename: str, content_type: str):
    time.sleep(5)

    return f"User {user_id} uploaded a '{content_type}' file '{filename}'"
