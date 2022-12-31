"""Main entry point for the FastAPI application.
"""

from fastapi import Depends, FastAPI, status
from sqlmodel import Session

from .core import database, models
from .core.database import get_session

app = FastAPI()


@app.on_event("startup")
def on_startup():
    database.create_tables()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/users/", response_model=models.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_create: models.UserCreate, session: Session = Depends(get_session)):
    user = database.add_user(user_create, session)
    return user


@app.get("/users/", response_model=list[models.UserRead])
def get_users(session: Session = Depends(get_session)):
    users = database.get_all_users(session)

    return users
