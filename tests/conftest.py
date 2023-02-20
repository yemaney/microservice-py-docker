from typing import Dict, Generator, List

import pika
import pytest
from fastapi.testclient import TestClient
from pika.adapters.blocking_connection import BlockingChannel
from sqlmodel import Session, SQLModel, create_engine, select

from api.core import models
from api.core.config import settings
from api.core.database import get_session
from api.core.queue import get_queue_channel
from api.main import app
from fileserver.main import app as fileserver_app


@pytest.fixture
def session():

    DB_URL = f"postgresql://{settings.db_user}:{settings.db_password}@localhost:{settings.db_port}/{settings.db_name}"

    test_engine = create_engine(f"{DB_URL}")

    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def channel() -> Generator[BlockingChannel, None, None]:

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="files_test")
    yield channel
    connection.close()


@pytest.fixture
def client(session: Session, channel: BlockingChannel):
    def get_session_override():
        return session

    def get_channel_override():
        return channel

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_queue_channel] = get_channel_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def fileserver_client():
    content_client = TestClient(fileserver_app)
    yield content_client


@pytest.fixture
def users(session: Session, client: TestClient):
    user_dicts: List[Dict[str, str]] = [
        {"email": "user1@email.com", "password": "123"},
        {"email": "user2@email.com", "password": "456"},
        {"email": "user3@email.com", "password": "789"},
    ]

    for user_dict in user_dicts:
        client.post("/users/", json=user_dict)
    user_models: List[models.UserCreate] = [models.UserCreate(**user) for user in user_dicts]  # type: ignore

    yield user_models
    for user_model in user_models:
        statement = select(models.User).where(models.User.email == user_model.email)
        results = session.exec(statement)
        user = results.one()
        session.delete(user)
    session.commit()


@pytest.fixture
def logged_in_user(client: TestClient, users: List[models.UserCreate]):
    user_dict = {"email": "user1@email.com", "password": "123"}
    client.post("/users", json=user_dict)

    user_dict["username"] = user_dict.pop("email")
    response = client.post("/login", data=user_dict)

    yield response.json(), users
