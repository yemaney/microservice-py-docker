"""This module is concerned with handling settings with environment variables.

The settings are created using a Pydantic class that reads environment variables from a `.env` file in the
`/api` directory if it is available.

Example `.env` file:
```
DB_USER=postgres
DB_PASSWORD=123
DB_HOST=postgres
DB_PORT=5432
DB_NAME=fastapi
```

Although it is recommended to use a .env file if deploying docker-compose, the settings will also read from
environment variables that are defined in the current terminal session.

Example creating the environment variables through the terminal:
`$ export DB_USER=postgres`
"""
from pydantic import BaseSettings


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minute: int

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
