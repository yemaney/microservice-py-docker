"""This module defines a router for the api that is dedicated to file related responsibilities."""

import logging
from typing import Annotated

import celery.exceptions
from celery.exceptions import TaskError
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from minio.error import S3Error

from api.core import celery, files, models, oauth2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/", response_model=models.UploadedFile, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],
    minio_client: Annotated[files.Minio, Depends(files.get_minio_client)],
    celery_client: Annotated[celery.Celery, Depends(celery.get_celery_client)],
):
    """
    Endpoint for uploading files.

    Parameters
    ----------
    file : UploadFile
        The file to be uploaded.
    current_user : models.User
        The current authenticated user.
    minio_client : files.Minio
        The MinIO client for interacting with the object storage.
    celery_client : celery.Celery
        The Celery client for queuing tasks.

    Returns
    -------
    dict
        A dictionary containing file metadata and status.

    Raises
    ------
    HTTPException
        If the file type is not supported or if there are errors during file upload or queuing.
    """
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type of {file.content_type} is not a supported media type of text/plain",
        )

    file_size = files.get_file_size(file)

    try:
        minio_client.put_object(files.BUCKET, f"{current_user.id}/{file.filename}", file.file, file_size)
    except S3Error as e:
        logger.exception("Error uploading file %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file.",
        ) from e

    try:
        # send file meta-data and user id to task queue
        task = celery_client.send_task(
            name="process_file",
            args=[current_user.id, file.filename, file.content_type],
        )
    except TaskError as e:
        logger.exception("Error queueing file process for %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error queueing file process",
        ) from e

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file_size,
        "status": task.status,
    }
