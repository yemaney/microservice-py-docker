from fastapi.testclient import TestClient
from sqlmodel import Session, select

from api.core import models


def test_login_success(session: Session, client: TestClient):

    payload = {"email": "user@email.com", "password": "password"}
    client.post("/users/", json=payload)

    response = client.post("/auth/login", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "user@email.com"

    user = session.exec(
        select(models.User).where(models.User.email == payload["email"])
    ).one()
    session.delete(user)
    session.commit()


def test_login_email_fail(session: Session, client: TestClient):

    payload = {"email": "correct@email.com", "password": "correct password"}
    client.post("/users/", json=payload)

    payload["email"] = "wrong@email.com"
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 403

    user = session.exec(
        select(models.User).where(models.User.email == "correct@email.com")
    ).one()
    session.delete(user)
    session.commit()


def test_login_password_fail(session: Session, client: TestClient):

    payload = {"email": "correct@email.com", "password": "correct password"}
    client.post("/users/", json=payload)

    payload["password"] = "wrong password"
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 403

    user = session.exec(
        select(models.User).where(models.User.email == "correct@email.com")
    ).one()
    session.delete(user)
    session.commit()
