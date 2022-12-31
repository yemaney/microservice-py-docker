from fastapi.testclient import TestClient
from sqlmodel import Session, select

from api.core import models


def test_create_user(session: Session, client: TestClient):

    user = models.User(email="user@email.com", password="password")
    session.add(user)
    session.commit()

    payload = {"email": "user@email.com", "password": "password"}

    response = client.post("/auth/login", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "user@email.com"

    statement = select(models.User).where(models.User.email == "user@email.com")
    results = session.exec(statement)
    hero = results.one()
    session.delete(hero)
    session.commit()
