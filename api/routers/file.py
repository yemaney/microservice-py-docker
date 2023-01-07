from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from ..core import models, oauth2

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def upload_file(file: UploadFile, current_user: models.User = Depends(oauth2.get_current_user)):

    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type of {file.content_type} is not a supported media type of text/plain",
        )

    return {"filename": file.filename, "content_type": file.content_type}
