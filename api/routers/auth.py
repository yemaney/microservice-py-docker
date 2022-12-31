from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core import database, models, utils
from ..core.database import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=models.UserRead)
def login(user: models.UserLogin, session: Session = Depends(get_session)):

    _user = None
    try:
        _user = database.get_user(user, session)
    except Exception:

        if not _user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
            )
    password_matching = utils.verify(user.password, _user.password)

    if not password_matching:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    return _user
