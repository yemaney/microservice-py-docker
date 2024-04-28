"""This module is concerned with functions and objects related to file handling."""

from fastapi import UploadFile
from minio import Minio

from api.core.config import settings

BUCKET = "images"


def get_minio_client(host: str = "minio") -> Minio:
    """
    get_minio_client creates and returns a client that can connect with the minIO

    Parameters
    ----------
    host : str, optional
        host to connect client to, by default "minio"

    Returns
    -------
    Minio
        client to interact with minIO service
    """
    client = Minio(
        f"{host}:9000",
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=False,  # Set to True if you use HTTPS.
    )

    # Make a bucket if it doesn't already exist.
    found = client.bucket_exists(BUCKET)
    if not found:
        client.make_bucket(BUCKET)

    return client


async def get_file_size(file: UploadFile) -> int:
    """
    get_file_size calculates the size of an uploaded file.

    This is required as the minIO client put_object method requires the length
    of the object being uploaded as one of the parameters.

    Parameters
    ----------
    file : UploadFile
        file of supported file type that user uploads

    Returns
    -------
    int
        size of the uploaded file
    """

    # Seek to the end of the file to get the file size
    file.file.seek(0, 2)  # Move the cursor to the end of the file
    file_size = file.file.tell()
    file.file.seek(0, 0)  # Move the cursor to the start of the file
    return file_size
