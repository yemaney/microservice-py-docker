from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core import database, models, utils
from ..core.database import get_session

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=models.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_create: models.UserCreate, session: Session = Depends(get_session)):
    user_exists = database.get_user(user_create, session)

    if user_exists:
        print(f"**** {user_exists = } **** ")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {user_create.email} already exists",
        )
    else:
        user_create.password = utils.hash_password(user_create.password)
        user = database.add_user(user_create, session)

        return user


@router.get("/", response_model=list[models.UserRead])
def get_users(session: Session = Depends(get_session)):
    users = database.get_all_users(session)

    return users
