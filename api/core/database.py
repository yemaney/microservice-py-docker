"""This module is concerned with database related operations.

Does:
- creates engine connected to database
- create database tables
- create temporary session connection to database
- add user to database
"""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine, select

from . import models
from .config import settings

DB_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
engine = create_engine(DB_URL, echo=True)


def create_tables() -> None:
    """populates database with all tables defined in models.py"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """yields a temporary session to the database"""
    with Session(engine) as session:
        yield session


def add_user(user_create: models.UserCreate, session: Session) -> models.User:
    """adds a user to the database"""
    user: models.User = models.User.from_orm(user_create)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_all_users(session: Session) -> list[models.User]:
    user = session.exec(select(models.User)).all()
    return user
