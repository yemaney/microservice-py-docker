"""This module is concerned with handling settings with environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings _summary_

    Attributes
    ----------
    db_user : str
        Database user name.

    db_password : str
        Database password.

    db_host : str
        Database host address.

    db_port : str
        Database port number.

    db_name : str
        Database name.

    secret_key : str
        Secret key for token generation.

    algorithm : str
        Algorithm used for token generation.

    access_token_expire_minute : int
        Time in minutes for access token expiration.

    minio_root_user : str
        The access key for MinIO.

    minio_root_password str
        The secret key for MinIO.

    default_user : str
        The username for RabbitMQ.

    default_pass : str
        The password for RabbitMQ.

    openrouter_api_key : str
        The API key for OpenRouter.

    Classes
    -------
        Config: Used to load values for this class from the .env file

    """

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str
    secret_key: str
    algorithm: str
    access_token_expire_minute: int
    minio_root_user: str
    minio_root_password: str
    minio_host: str = "minio"
    default_user: str
    default_pass: str
    openrouter_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
