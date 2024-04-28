from fastapi import status
from fastapi.testclient import TestClient


def test_root(client: TestClient):
    r = client.get("/")
    assert r.status_code == status.HTTP_200_OK


def test_healthcheck(client: TestClient):
    r = client.get("/healthcheck")

    assert r.json()["status"] == "OK"
    assert r.status_code == status.HTTP_200_OK
