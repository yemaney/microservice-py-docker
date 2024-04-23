"""This module defines a router for the api that is dedicated to file related responsibilities."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from ..core import celery, files, models, oauth2

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    current_user: models.User = Depends(oauth2.get_current_user),
    minio_client: files.Minio = Depends(files.get_minio_client),
    celery_client: celery.Celery = Depends(celery.get_celery_client),
):
    """Endpoint for users to upload one file. Checks content type to make sure its supported,
    otherwise returns an `415` HTTP error code. Sends the uploaded file to the minIO server
    and then sends a task message to the celery queue for further processing.

    This endpoint requires authorization in the form of a bearer token in the headers of the
    request.

    Parameters
    ----------
    file : UploadFile
        file of supported file type that user uploads
    current_user : models.User
        authorized user, by default Depends(oauth2.get_current_user)
    minio_client : files.Minio
        client used to upload files to the minIO service, by default Depends(files.Minio)
    celery_client : celery.Celery
        client used to send tasks to the broker queue, by default Depends(celery.client)
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
        minio_client.put_object(
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
        # send file meta-data and user id to task queue
        task = celery_client.send_task(
            name="process_file",
            args=[current_user.id, file.filename, file.content_type],
        )
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
        "status": task.status,
    }
