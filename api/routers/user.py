"""This module defines router for the api that is dedicated to user related responsibilities."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.core import database, models, oauth2

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=models.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_create: models.UserCreate,
    session: Annotated[Session, Depends(database.get_session)],
):
    """
    Endpoint for creating a new user.

    Parameters
    ----------
    user_create : models.UserCreate
        The data required to create a new user.
    session : Session
        The session to interact with the database.

    Returns
    -------
    models.UserRead
        The created user data to be read.

    Raises
    ------
    HTTPException
        If a user with the same email already exists, raises status code 409 (CONFLICT).
    """
    user_exists = database.get_user(user_create.email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {user_create.email} already exists",
        )
    user_create.password = oauth2.hash_password(user_create.password)
    return database.add_user(user_create, session)


@router.get("/", response_model=list[models.UserRead])
def get_users(
    session: Annotated[Session, Depends(database.get_session)],
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],  # noqa: ARG001
):
    """
    Endpoint for retrieving all users.

    Parameters
    ----------
    session : Session
        The session to interact with the database.
    current_user : models.User
        The current authenticated user.

    Returns
    -------
    list[models.UserRead]
        A list of user data to be read.
    """
    return database.get_all_users(session)
