import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from api.core import models
from api.core.config import settings
from api.core.database import get_session
from api.main import app


@pytest.fixture(name="session")
def session_fixture():

    DB_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    test_engine = create_engine(f"{DB_URL}_test")

    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="users")
def users_fixture(session: Session, client: TestClient):
    user_dicts: list[dict[str, str]] = [
        {"email": "user1@email.com", "password": "123"},
        {"email": "user2@email.com", "password": "456"},
        {"email": "user3@email.com", "password": "789"},
    ]

    for user_dict in user_dicts:
        client.post("/users/", json=user_dict)
    user_models: list[models.User] = [models.User(**user) for user in user_dicts]

    yield user_models
    for user_model in user_models:
        statement = select(models.User).where(models.User.email == user_model.email)
        results = session.exec(statement)
        user = results.one()
        session.delete(user)
    session.commit()
