from fastapi.testclient import TestClient

from api.core import models


def test_login_success(client: TestClient, users: list[models.UserCreate]):
    payload = {"email": users[0].email, "password": users[0].password}
    response = client.post("/auth/login", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "user1@email.com"


def test_login_email_fail(client: TestClient, users: list[models.UserCreate]):
    payload = {"email": "wrong@email.com", "password": users[0].password}

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 403


def test_login_password_fail(client: TestClient, users: list[models.UserCreate]):

    payload = {"email": users[0].email, "password": "wrong password"}

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 403
