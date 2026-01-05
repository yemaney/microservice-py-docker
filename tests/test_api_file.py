import tempfile

from fastapi import status
from fastapi.testclient import TestClient

from api.core import models


def test_upload_file(client: TestClient, logged_in_user: tuple[dict, list[models.UserCreate]]):
    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}

    with tempfile.TemporaryFile() as fp:
        files = [("file", ("my_file.txt", fp, "text/plain"))]
        response = client.post("/files", headers=headers, files=files)

        data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert data["filename"] == "my_file.txt"
        assert data["content_type"] == "text/plain"


def test_upload_filetype_fail(client: TestClient, logged_in_user: tuple[dict, list[models.UserCreate]]):
    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}

    with tempfile.TemporaryFile() as fp:
        files = [("file", ("my_file.txt", fp, "image/gif"))]
        response = client.post("/files", headers=headers, files=files)

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_upload_file_auth_fail(client: TestClient):
    with tempfile.TemporaryFile() as fp:
        files = [("file", ("my_file.txt", fp, "text/plain"))]
        response = client.post("/files", files=files)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
