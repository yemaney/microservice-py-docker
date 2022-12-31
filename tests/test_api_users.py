from fastapi.testclient import TestClient
from sqlmodel import Session, select

from api.core import models


def test_create_user(session: Session, client: TestClient):
    payload = {"email": "user@email.com", "password": "password"}

    response = client.post("/users/", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["email"] == "user@email.com"

    statement = select(models.User).where(models.User.email == "user@email.com")
    results = session.exec(statement)
    hero = results.one()
    session.delete(hero)
    session.commit()


def test_read_heroes(session: Session, client: TestClient):
    user_1 = models.User(email="user1@email.com", password="123")
    user_2 = models.User(email="user2@email.com", password="456")
    user_3 = models.User(email="user3@email.com", password="789")
    session.add(user_1)
    session.add(user_2)
    session.add(user_3)
    session.commit()

    response = client.get("/users/")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 3
    assert data[0]["email"] == user_1.email
    assert data[1]["email"] == user_2.email
    assert data[2]["email"] == user_3.email

    session.delete(user_1)
    session.delete(user_2)
    session.delete(user_3)
    session.commit()
