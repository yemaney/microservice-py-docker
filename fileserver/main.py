"""Main entry point for the file-server FastAPI application.
"""

import logging
import os
import shutil
import sys
from typing import Union

from fastapi import FastAPI, Header, UploadFile, status


def get_logger(name: str = "backend") -> logging.Logger:
    """Define a standard logger for the project"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # set logger level
    logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    consoleHandler = logging.StreamHandler(sys.stdout)  # set streamhandler to stdout
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    return logger


logger = get_logger()
app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/file", status_code=status.HTTP_201_CREATED)
def upload_file(file: UploadFile, user_id: Union[str, None] = Header(default=None)):
    """
    Endpoint that receives fils from the api service. Saves the file to a user
    specific folder in disk.

    Not intended to be used directly. Rather that be interacted only through the api
    service.

    Parameters
    ----------
    file : UploadFile
        file that is sent by the api service
    user_id : Union[str, None], optional
        the id of the user that owns the file, by default Header(default=None)

    Returns
    -------
    dict
        dictionary containing the filename and content type
    """
    logger.info(f"{user_id} uploaded {file.filename}")

    try:
        # make sure folder exists
        file_path = f"./fileserver/files/{user_id}"
        os.makedirs(file_path, exist_ok=True)

        # save file to disk
        with open(f"{file_path}/{file.filename}", "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        logger.error(e)
        return {"status": 500, "filename": file.filename, "content_type": file.content_type}
    return {"filename": file.filename, "content_type": file.content_type}
