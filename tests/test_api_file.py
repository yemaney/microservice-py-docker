import tempfile
from typing import List, Tuple

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlmodel import Session

from api.core import models
from api.core.database import get_session
from api.main import app


@pytest.mark.anyio
async def test_upload_file(session: Session, logged_in_user: Tuple[dict, List[models.UserCreate]]):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}

    with tempfile.TemporaryFile() as fp:
        files = [("file", ("my_file.txt", fp, "text/plain"))]
        async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
            response = await ac.post("/files/", headers=headers, files=files, data={})

        data = response.json()
        assert response.status_code == 201
        assert data["filename"] == "my_file.txt"
        assert data["content_type"] == "text/plain"


def test_upload_filetype_fail(client: TestClient, logged_in_user: Tuple[dict, List[models.UserCreate]]):
    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}

    with tempfile.TemporaryFile() as fp:
        files = [("file", ("my_file.txt", fp, "image/gif"))]
        response = client.post("/files", headers=headers, files=files)

        assert response.status_code == 415


def test_upload_file_auth_fail(client: TestClient):

    with tempfile.TemporaryFile() as fp:
        files = [("file", ("my_file.txt", fp, "text/plain"))]
        response = client.post("/files", files=files)

        assert response.status_code == 401
