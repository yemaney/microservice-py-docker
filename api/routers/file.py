"""This module defines a router for the api that is dedicated to file related responsibilities.
"""
import json

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from ..core import models, oauth2, queue

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    current_user: models.User = Depends(oauth2.get_current_user),
    channel: queue.BlockingChannel = Depends(queue.get_queue_channel),
):
    """
    Endpoint for users to upload one file. Checks content type to make sure its supported,
    otherwise returns an `415` HTTP error code. Sends the uploaded file to the file server
    and then sends a message to the file queue for further processing.

    This endpoint requires authorization in the form of a bearer token in the headers of the
    request.

    Parameters
    ----------
    file : UploadFile
        file of supported file type that user uploads
    current_user : models.User
        authorized user, by default Depends(oauth2.get_current_user)
    channel : queue.BlockingChannel
        channel used to publish message to file queue, by default Depends(queue.get_queue_channel)

    Returns
    -------
    dict
        if successful, returns a dictionary containing the uploaded files filename and content type

    Raises
    ------
    HTTPException
        if file with unsupported content type is uploaded
    """
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type of {file.content_type} is not a supported media type of text/plain",
        )

    # send file to file-server
    # include user id in headers
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://127.0.0.1:8080/file",
            data={},
            files={"file": (file.filename, file.file)},
            headers={"user-id": str(current_user.id)},
        )

    # send file meta-data to queue
    message = {"filename": file.filename, "content_type": file.content_type}
    channel.basic_publish(exchange="", routing_key="files", body=json.dumps(message))

    return {"filename": file.filename, "content_type": file.content_type}
