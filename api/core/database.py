"""This module is concerned with database related operations.

Does:
- creates engine connected to database
- create database tables
- create temporary session connection to database
- add user to database
"""

from sqlmodel import Session, SQLModel, create_engine

from . import models
from .config import settings

DB_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
engine = create_engine(DB_URL, echo=True)


def create_tables():
    """populates database with all tables defined in models.py"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """yields a temporary session to the database"""
    with Session(engine) as session:
        yield session


def add_user(user_create: models.UserCreate, session: Session):
    """adds a user to the database"""
    user: models.User = models.User.from_orm(user_create)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
