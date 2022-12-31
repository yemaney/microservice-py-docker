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


def test_read_heroes(client: TestClient, users: list[models.User]):

    response = client.get("/users/")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 3
    assert data[0]["email"] == users[0].email
    assert data[1]["email"] == users[1].email
    assert data[2]["email"] == users[2].email
