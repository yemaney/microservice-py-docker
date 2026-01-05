from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.core import models


@pytest.fixture
def mock_embeddings():
    with patch("api.core.embeddings.generate_embedding", new_callable=AsyncMock) as mock:
        mock.return_value = [0.1] * 4096  # Mock embedding vector with 4096 dimensions
        yield mock


def test_search_files_success(
    client: TestClient,
    logged_in_user: tuple[dict, list[models.UserCreate]],
    session: Session,
    mock_embeddings,
):
    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}

    # Create file metadata directly in the database for test isolation
    user_email = logged_in_user[1][0].email
    user = session.query(models.User).filter(models.User.email == user_email).first()

    file_name = "test_document.txt"
    test_file = models.FileMetadata(
        user_id=user.id,
        filename=file_name,
        content_type="text/plain",
        size=100,
        minio_path=f"{user.id}/{file_name}",
        embedding=[0.1] * 4096,
    )
    session.add(test_file)
    session.commit()

    # Perform search
    response = client.get("/search/files?query=test", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(item["filename"] == file_name for item in data)

    # Find the specific file in results to verify details
    search_result = next(item for item in data if item["filename"] == file_name)
    assert "similarity" in search_result
    assert search_result["user_id"] == user.id

    # Verify the mock was called
    mock_embeddings.assert_called_once()

    # Cleanup test data
    session.delete(test_file)
    session.commit()


def test_search_files_unauthorized(client: TestClient):
    response = client.get("/search/files?query=test")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_find_similar_files_success(
    client: TestClient,
    logged_in_user: tuple[dict, list[models.UserCreate]],
    session: Session,
    mock_embeddings,
):
    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}

    # Get the logged-in user
    user_email = logged_in_user[1][0].email
    user = session.query(models.User).filter(models.User.email == user_email).first()

    # Create multiple test files with different embeddings
    target_file = models.FileMetadata(
        user_id=user.id,
        filename="target_file.txt",
        content_type="text/plain",
        size=100,
        minio_path=f"{user.id}/target_file.txt",
        embedding=[0.1] * 4096,
    )
    session.add(target_file)
    session.commit()
    session.refresh(target_file)

    # Create similar file (same embedding)
    similar_file = models.FileMetadata(
        user_id=user.id,
        filename="similar_file.txt",
        content_type="text/plain",
        size=150,
        minio_path=f"{user.id}/similar_file.txt",
        embedding=[0.1] * 4096,
    )
    session.add(similar_file)

    # Create dissimilar file (different embedding)
    dissimilar_file = models.FileMetadata(
        user_id=user.id,
        filename="dissimilar_file.txt",
        content_type="text/plain",
        size=200,
        minio_path=f"{user.id}/dissimilar_file.txt",
        embedding=[0.9] * 4096,
    )
    session.add(dissimilar_file)
    session.commit()

    # Find similar files
    response = client.get(f"/search/files/similar/{target_file.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify the target file is not in the results
    assert not any(item["id"] == target_file.id for item in data)

    # Verify similar files are returned
    assert any(item["filename"] == "similar_file.txt" for item in data)

    # Verify similarity scores are present
    for item in data:
        assert "similarity" in item
        assert 0 <= item["similarity"] <= 1

    # Verify the mock was not called (using existing embeddings from DB)
    mock_embeddings.assert_not_called()

    # Cleanup test data
    session.delete(target_file)
    session.delete(similar_file)
    session.delete(dissimilar_file)
    session.commit()


def test_find_similar_files_not_found(
    client: TestClient,
    logged_in_user: tuple[dict, list[models.UserCreate]],
):
    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}

    # Try to find similar files for a non-existent file
    response = client.get("/search/files/similar/99999", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_find_similar_files_unauthorized(client: TestClient):
    response = client.get("/search/files/similar/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_find_similar_files_access_denied(
    client: TestClient,
    logged_in_user: tuple[dict, list[models.UserCreate]],
    session: Session,
    mock_embeddings,
):
    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}

    # Get a different user
    user_email = logged_in_user[1][1].email
    other_user = session.query(models.User).filter(models.User.email == user_email).first()

    # Create a file for the other user
    other_user_file = models.FileMetadata(
        user_id=other_user.id,
        filename="other_user_file.txt",
        content_type="text/plain",
        size=100,
        minio_path=f"{other_user.id}/other_user_file.txt",
        embedding=[0.1] * 4096,
    )
    session.add(other_user_file)
    session.commit()
    session.refresh(other_user_file)

    # Try to find similar files for another user's file
    response = client.get(f"/search/files/similar/{other_user_file.id}", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

    # Verify the mock was not called
    mock_embeddings.assert_not_called()

    # Cleanup test data
    session.delete(other_user_file)
    session.commit()
