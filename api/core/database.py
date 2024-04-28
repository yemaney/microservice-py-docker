"""This module is concerned with database related operations."""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine, select

from api.core import models
from api.core.config import settings

DB_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
engine = create_engine(DB_URL)


def create_tables() -> None:
    """populates database with all tables defined in models.py"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Yields a temporary session to the database.

    Yields
    ------
    Session
        A temporary session to interact with the database.
    """
    with Session(engine) as session:
        yield session


def add_user(user_create: models.UserCreate, session: Session) -> models.User:
    """
    Adds a user to the database.

    Parameters
    ----------
    user_create : models.UserCreate
        The data required to create a new user.
    session : Session
        The session to interact with the database.

    Returns
    -------
    models.User
        The user added to the database.
    """
    user: models.User = models.User.from_orm(user_create)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_all_users(session: Session) -> list[models.User]:
    """
    Retrieve all users from the database.

    Parameters
    ----------
    session : Session
        The session to interact with the database.

    Returns
    -------
    list[models.User]
        A list of all users in the database.
    """

    return session.exec(select(models.User)).all()


def get_user(email: str, session: Session) -> models.User | None:
    """
    Retrieve one user from the database based on email match.

    Parameters
    ----------
    email : str
        The email address of the user to retrieve.
    session : Session
        The session to interact with the database.

    Returns
    -------
    models.User | None
        The user with the specified email if found, otherwise None.
    """

    return session.exec(select(models.User).where(models.User.email == email)).first()
