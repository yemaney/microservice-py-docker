from typing import List

from fastapi import status
from fastapi.testclient import TestClient

from api.core import models


def test_login_success(client: TestClient, users: List[models.UserCreate]):
    payload = {"username": users[0].email, "password": users[0].password}
    response = client.post("/login", data=payload)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in data
    assert data["token_type"] == "bearer"  # noqa: S105


def test_login_email_fail(client: TestClient, users: List[models.UserCreate]):
    payload = {"username": "wrong@email.com", "password": users[0].password}

    response = client.post("/login", data=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_login_password_fail(client: TestClient, users: List[models.UserCreate]):
    payload = {"username": users[0].email, "password": "wrong password"}

    response = client.post("/login", data=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
