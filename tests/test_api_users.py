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
    payload = {"email": "user1@email.com", "password": "password"}

    response = client.post("/users/", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["email"] == "user1@email.com"


def test_read_heroes(session: Session, client: TestClient):
    user_2 = models.User(email="user2@email.com", password="123")
    user_3 = models.User(email="user3@email.com", password="456")
    user_4 = models.User(email="user4@email.com", password="123")
    user_5 = models.User(email="user5@email.com", password="456")
    session.add(user_2)
    session.add(user_3)
    session.add(user_4)
    session.add(user_5)
    session.commit()

    response = client.get("/users/")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 5
    assert data[0]["email"] == "user1@email.com"  # from test_create_user
    assert data[1]["email"] == user_2.email
    assert data[2]["email"] == user_3.email
    assert data[3]["email"] == user_4.email
    assert data[4]["email"] == user_5.email
