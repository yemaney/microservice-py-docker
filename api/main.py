"""Main entry point for the FastAPI application.
"""

from fastapi import FastAPI

from .core import database
from .routers import user

app = FastAPI()

app.include_router(user.router)


@app.on_event("startup")
def on_startup():
    database.create_tables()


@app.get("/")
def root():
    return {"message": "Hello World"}
