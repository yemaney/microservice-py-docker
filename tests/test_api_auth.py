from fastapi.testclient import TestClient

from api.core import models


def test_login_success(client: TestClient, users: list[models.User]):

    response = client.post("/auth/login", json=users[0].dict())
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "user1@email.com"


def test_login_email_fail(client: TestClient, users: list[models.User]):

    payload = users[0].dict()

    payload["email"] = "wrong@email.com"
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 403


def test_login_password_fail(client: TestClient, users: list[models.User]):

    payload = users[0].dict()

    payload["password"] = "wrong password"
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 403
