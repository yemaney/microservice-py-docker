"""This module is concerned with authentication and security related operations."""

import datetime
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from api.core import database, models
from api.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    """
    Creates a JWT token that will later be used by users to authenticate their requests.

    Parameters
    ----------
    data : dict
        The payload data to be encoded into the token.

    Returns
    -------
    str
        The encoded JWT token.
    """
    to_encode = data.copy()

    expire = datetime.datetime.now(datetime.UTC) + timedelta(minutes=settings.access_token_expire_minute)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_access_token(token: str, credentials_exception: HTTPException):
    """
    Verifies a JWT token has been encrypted using the application's secret key,
    has the expected data in the payload, and hasn't expired yet.

    Parameters
    ----------
    token : str
        The JWT token to be verified.
    credentials_exception : HTTPException
        The exception to be raised if credentials cannot be validated.

    Raises
    ------
    HTTPException
        If the token cannot be decoded or does not contain the expected user ID,
        raises the provided credentials exception.

    Returns
    -------
    str
        The user ID extracted from the token payload.

    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        _id = payload.get("user")
        if _id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e
    return _id


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(database.get_session)],
) -> models.User | None:
    """
    Gets the current user by verifying the JWT token passed and using its payload data
    to query the users database for a corresponding user.

    Parameters
    ----------
    token : str
        The JWT token used for authentication (default is obtained from `oauth2_scheme`).
    session : Session
        The session to interact with the database (default is obtained from `database.get_session`).

    Raises
    ------
    HTTPException
        If credentials cannot be validated, returns status code 401 (UNAUTHORIZED) with a detail message.
        The response header contains the WWW-Authenticate field set to 'Bearer'.

    Returns
    -------
    models.User | None
        The user corresponding to the provided token, if found; otherwise, returns None.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    _id = verify_access_token(token, credentials_exception)

    return session.exec(select(models.User).where(models.User.id == _id)).first()


def hash_password(password: str) -> str:
    """
    Hashes plain text password.

    Parameters
    ----------
    password : str
        The plaintext password to be hashed.

    Returns
    -------
    str
        The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plaintext password against hashed password in the database.

    Parameters
    ----------
    plain_password : str
        The plaintext password to be verified.
    hashed_password : str
        The hashed password stored in the database.

    Returns
    -------
    bool
        True if the plaintext password matches the hashed password; otherwise, False.
    """
    return pwd_context.verify(plain_password, hashed_password)
