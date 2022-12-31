"""This module is concerned with creating models used for both table creation and data validation.

The classes with `table=True` are used to define tables that will be created in the database.

The rest of the classes are used for schema validation: They are used to control what data the api
endpoints can receive and return. If the data doesn't match the schema at either end of the api journey
then an error will occur.
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: str


class User(UserBase, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    pass
