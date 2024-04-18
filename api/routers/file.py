"""This module defines a router for the api that is dedicated to file related responsibilities."""

import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from ..core import files, models, oauth2, queue

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    current_user: models.User = Depends(oauth2.get_current_user),
    client: files.Minio = Depends(files.get_minio_client),
    message_publisher: queue.Awaitable = Depends(queue.get_publisher),
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
    client : files.Minio
        client used to upload files to the minIO service
    message_publisher : queue.BlockingChannel
        channel used to publish message to file queue, by default Depends(queue.get_publisher)
    Returns
    -------
    dict
        if successful, returns a dictionary containing the uploaded files filename and content type

    Raises
    ------
    HTTPException
        if file content type is unsupported or the client couldn't upload to minIO
    """
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type of {file.content_type} is not a supported media type of text/plain",
        )

    file_size = await files.get_file_size(file)

    try:
        client.put_object(
            files.BUCKET, f"{current_user.id}/{file.filename}", file.file, file_size
        )
        print(
            f"'{file.filename}' is successfully uploaded as '{file.filename}' in bucket '{files.BUCKET}'."
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file.",
        )

    try:
        # send file meta-data to queue
        message = {"filename": file.filename, "content_type": file.content_type}
        await message_publisher(message)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error queueing file process",
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file_size,
        "date": datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
    }
