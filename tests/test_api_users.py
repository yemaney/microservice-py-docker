import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from api.core import models
from api.core.config import settings
from api.core.database import get_session
from api.main import app

client = TestClient(app)


@pytest.fixture(name="session")
def session_fixture():

    DB_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    test_engine = create_engine(f"{DB_URL}_test", echo=True)

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


def test_create_user(client: TestClient):
    payload = {"email": "user@email.com", "password": "password"}

    r = client.post("/users/", json=payload)

    assert r.status_code == 201

    r_user = models.UserRead(**r.json())
    assert r_user.email == "user@email.com"
