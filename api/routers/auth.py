"""This module defines a router for the api that is dedicated to authentication."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import Session

from api.core import database, models, oauth2

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=models.Token)
def login(
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(database.get_session)],
):
    """
    Endpoint for user login. Returns a JWT token upon successful authentication.

    Parameters
    ----------
    user_credentials : OAuth2PasswordRequestForm
        The user's credentials (username and password) obtained from the request.
    session : Session
        The session to interact with the database.

    Raises
    ------
    HTTPException
        If the credentials are invalid, raises status code 403 (FORBIDDEN) with appropriate detail.

    Returns
    -------
    models.Token
        The JWT token and its type upon successful authentication.
    """
    user = database.get_user(user_credentials.username, session)

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    password_matching = oauth2.verify_password(user_credentials.password, user.password)
    if not password_matching:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
