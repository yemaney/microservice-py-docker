"""This module is concerned with creating models used for both table creation and data validation.

The classes with `table=True` are used to define tables that will be created in the database.

The rest of the classes are used for schema validation: They are used to control what data the api
endpoints can receive and return. If the data doesn't match the schema at either end of the api journey
then an error will occur.

**Note** : Plain SQLModels effectively act as Pydantic Models
"""

from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, EmailStr
from sqlmodel import AutoString, Field, SQLModel


class UserBase(SQLModel):
    """
    Represents the base attributes of a user.

    Attributes
    ----------
    email : EmailStr
        The email address of the user. It should be unique.

    """

    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)


class User(UserBase, table=True):  # type: ignore
    """
    Represents a user entity, inheriting from UserBase.

    Attributes
    ----------
    id : Optional[int]
        The unique identifier of the user. It is a primary key.
    password : str
        The hashed password of the user.
    created_at : Optional[datetime]
        The datetime when the user account was created. Defaults to the current UTC time.

    """

    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=False)


class UserCreate(UserBase):
    """
    Represents the data required to create a new user.

    Attributes
    ----------
    email : EmailStr
        The email address of the user. It should be unique.
    password : str
        The plaintext password of the user.

    """

    password: str


class UserRead(UserBase):
    """
    Represents the data of a user to be read.

    Attributes
    ----------
    email : EmailStr
        The email address of the user. It should be unique.
    created_at : datetime
        The datetime when the user account was created.

    """

    created_at: datetime


class UserLogin(UserCreate):
    """
    Represents the data required for user login, inheriting from UserCreate.

    Attributes
    ----------
    email : EmailStr
        The email address of the user. It should be unique.
    password : str
        The plaintext password of the user.

    """


class Token(SQLModel):
    """
    Represents a token entity returned when a user requests one.

    Attributes
    ----------
    access_token : str
        The access token string.
    token_type : str
        The type of the token.

    """

    access_token: str
    token_type: str


class HealthCheck(BaseModel):
    """
    Response model to validate and return when performing a health check.

    Attributes
    ----------
    status : str
        The status of the health check. Default value is "OK".

    """

    status: str = "OK"


class UploadedFile(BaseModel):
    """
    Response model to return when file is uploaded.

    Attributes
    ----------
    filename : str
        The name of the uploaded file.
    size : int
        The size of the uploaded file.
    content_type : str
        The content type of the uploaded file.
    status : str
        The status of the uploaded file.

    """

    filename: str
    size: int
    content_type: str
    status: str


class FileMetadata(SQLModel, table=True):  # type: ignore
    """
    Represents metadata for uploaded files including vector embeddings.

    Attributes
    ----------
    id : Optional[int]
        The unique identifier of the file metadata. It is a primary key.
    user_id : int
        The ID of the user who uploaded the file.
    filename : str
        The name of the uploaded file.
    content_type : str
        The content type of the uploaded file.
    size : int
        The size of the uploaded file in bytes.
    minio_path : str
        The path to the file in MinIO storage.
    embedding : list[float]
        The vector embedding of the file content (4096 dimensions).
    created_at : Optional[datetime]
        The datetime when the file was uploaded. Defaults to the current UTC time.

    """

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    filename: str = Field(index=True)
    content_type: str
    size: int
    minio_path: str
    embedding: list[float] = Field(sa_type=Vector(4096))
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=False)


class FileSearchResult(BaseModel):
    """
    Response model for file search results.

    Attributes
    ----------
    id : int
        The unique identifier of the file metadata.
    filename : str
        The name of the file.
    content_type : str
        The content type of the file.
    size : int
        The size of the file in bytes.
    user_id : int
        The ID of the user who owns the file.
    created_at : datetime
        When the file was uploaded.
    similarity : float
        The similarity score between the search query and the file embedding.

    """

    id: int
    filename: str
    content_type: str
    size: int
    user_id: int
    created_at: datetime
    similarity: float
