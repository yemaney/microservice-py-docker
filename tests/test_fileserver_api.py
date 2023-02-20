import tempfile

from fastapi.testclient import TestClient


def test_upload_file(fileserver_client: TestClient):

    with tempfile.TemporaryFile() as fp:
        files = [("file", ("my_file.txt", fp, "text/plain"))]
        response = fileserver_client.post("/file", headers={"user": "1"}, files=files)
        data = response.json()

        assert response.status_code == 201
        assert data["filename"] == "my_file.txt"
        assert data["content_type"] == "text/plain"
