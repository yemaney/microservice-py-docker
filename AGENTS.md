# Agent Guide: Microservice Python Docker Project

This document provides a comprehensive overview of the microservice-py-docker codebase structure, conventions, and operational procedures.

## Project Overview

This is a Python-based microservice architecture using FastAPI, PostgreSQL, RabbitMQ, and MinIO, containerized with Docker and orchestrated via Docker Compose. The project follows modern Python development practices with comprehensive tooling for testing, linting, and documentation.

## Architecture

The project consists of four main services orchestrated via Docker Compose:

- **API Service**: FastAPI application providing REST endpoints (port 8000)
- **Backend Service**: Celery worker for asynchronous task processing
- **PostgreSQL**: Database service (port 5432)
- **RabbitMQ**: Message broker (ports 5672, 15672)
- **MinIO**: Object storage service (ports 9000, 9001)

### Directory Structure

```
microservice-py-docker/
├── api/                    # FastAPI application
│   ├── core/              # Core functionality
│   │   ├── celery.py      # Celery client configuration
│   │   ├── config.py      # Application settings
│   │   ├── database.py    # Database connection
│   │   ├── files.py       # MinIO client
│   │   ├── models.py      # SQLModel definitions
│   │   └── oauth2.py      # Authentication
│   ├── routers/           # API route handlers
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── file.py        # File operations
│   │   └── user.py        # User management
│   ├── Dockerfile         # API container config
│   └── main.py            # FastAPI application entry point
├── backend/               # Celery worker
│   ├── Dockerfile         # Backend container config
│   └── main.py            # Celery worker entry point
├── docs/                  # Documentation
│   ├── images/            # Documentation assets
│   ├── gen_ref_pages.py   # API reference generation
│   └── index.md           # Documentation homepage
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest configuration and fixtures
│   └── test_*.py          # Test modules
├── docker-compose.yml     # Service orchestration
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # Dependency lock file
├── requirements.txt      # Exported requirements (generated)
├── ruff.toml            # Linting configuration
├── mkdocs.yml           # Documentation configuration
├── .pre-commit-config.yaml # Pre-commit hooks
└── Makefile             # Build and development tasks
```

## Code Conventions

### Python Version
- **Python 3.12+** required
- Uses modern Python features and type hints throughout

### Linting and Formatting
- **Ruff** is used for both linting and formatting
- Configuration in `ruff.toml`:
  - Line length: 120 characters
  - Preview mode enabled for latest features
  - Extensive rule set covering style, performance, and security
  - `docs/` directory excluded from linting
  - Tests allowed to use `assert` statements (`S101` rule ignored)

### Naming Conventions
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Test functions: `test_descriptive_name`
- Modules: `snake_case`

### Documentation Style
- **NumPy docstring format** for all functions and classes
- Type hints used throughout codebase
- MkDocs with Material theme for documentation

## Testing

### Test Framework
- **pytest** as the testing framework
- Coverage reporting with **pytest-cov**
- Tests located in `tests/` directory

### Test Structure and Conventions

#### Configuration (`tests/conftest.py`)
```python
# Database session fixture for each test
@pytest.fixture
def session():
    # Creates test database connection
    # Yields session for use in tests

# FastAPI test client with dependency overrides
@pytest.fixture
def client(session: Session):
    # Overrides database, celery, and minio dependencies
    # Provides isolated test client

# User fixtures for authentication testing
@pytest.fixture
def users(session: Session, client: TestClient):
    # Creates test users
    # Cleans up after tests
```

#### Test File Organization
- Test files named `test_*.py`
- Test functions named `test_descriptive_action`
- Fixtures imported from `conftest.py`

#### Example Test Format
```python
def test_create_user(session: Session, client: TestClient):
    payload = {"email": "user@email.com", "password": "password"}

    response = client.post("/users/", json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data["email"] == "user@email.com"

    # Cleanup test data
    statement = select(models.User).where(models.User.email == "user@email.com")
    results = session.exec(statement)
    user = results.one()
    session.delete(user)
    session.commit()
```

### Running Tests

#### Individual Test Run
```bash
pytest
```

#### With Coverage
```bash
pytest --cov
```

#### Generate Coverage Badge
```bash
make badge
# Runs tests with coverage and generates docs/images/coverage.svg
```

#### Full CI Pipeline
```bash
make checks
# Runs: compose, tests, requirements sync, pre-commit
```

## Docker Compose Orchestration

### Service Dependencies
The `docker-compose.yml` defines service startup order with health checks:

```yaml
services:
  api:
    depends_on:
      postgres:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
      minio:
        condition: service_healthy
      backend:
        condition: service_healthy
```

### Starting Services
```bash
make compose
# Cleans up old images, then runs docker-compose up -d
```

### Service Health Checks
- **PostgreSQL**: Uses `pg_isready` command
- **RabbitMQ**: Uses `rabbitmq-diagnostics ping`
- **MinIO**: Uses health endpoint curl
- **Backend**: Uses `celery status` command
- **API**: Uses `/healthcheck` endpoint

### Environment Configuration
All services use `.env` file for configuration, loaded via `env_file` directive.

## Dependency Management with uv

### Package Manager
- **uv** is used as the Python package manager
- Faster than pip, with advanced dependency resolution

### Configuration (`pyproject.toml`)

#### Main Dependencies
```toml
[project]
dependencies = [
    "aio-pika==9.4.1",        # RabbitMQ client
    "celery==5.4.0",          # Task queue
    "fastapi[all]==0.110.2",  # Web framework
    "minio==7.2.6",           # Object storage
    "passlib==1.7.4",         # Password hashing
    "psycopg2-binary==2.9.9", # PostgreSQL driver
    "python-jose==3.3.0",     # JWT tokens
    "sqlmodel==0.0.16",       # ORM
]
```

#### Dependency Groups
```toml
[dependency-groups]
dev = [
    "pre-commit==2.21.0",
    "pytest==7.2.0",
    "pytest-cov==4.0.0",
    "trio==0.22.0",
]
docs = [
    "coverage-badge==1.1.0",
    "mkdocs-gen-files==0.5.0",
    "mkdocs-literate-nav==0.6.1",
    "mkdocs-material==8.5.11",
    "mkdocs-section-index==0.3.9",
    "mkdocstrings[python]==0.25.0",
]
```

### Commands

#### Install Dependencies
```bash
uv sync
```

#### Add New Dependency
```bash
uv add package-name
```

#### Add Development Dependency
```bash
uv add --group dev package-name
```

#### Export to requirements.txt
```bash
uv export --format requirements-txt > requirements.txt
```

#### Check Requirements Sync
```bash
make requirements
# Syncs dependencies and verifies requirements.txt is up-to-date
```

## Development Workflow

### Initial Setup
```bash
make init
# Installs uv, pipx, gitmoji, updates apt
```

### Pre-commit Hooks
Configuration in `.pre-commit-config.yaml`:
- **Ruff linting and formatting**
- **Codespell** for spell checking

Run pre-commit on all files:
```bash
pre-commit run --all-files
```

### Full Development Cycle
```bash
make checks
# Runs complete pipeline: compose → tests → requirements → pre-commit
```

## Documentation

### Documentation Framework
- **MkDocs** with Material theme
- **mkdocstrings** for automatic API documentation generation

### Configuration (`mkdocs.yml`)
- NumPy docstring style
- Source-ordered member documentation
- Signature annotations displayed
- Section index and literate navigation

### Building Documentation
```bash
mkdocs build
```

### Serving Documentation Locally
```bash
mkdocs serve
```

### API Reference Generation
- `docs/gen_ref_pages.py` automatically generates API reference pages
- Uses `mkdocstrings` plugin with Python handler

## Containerization

### API Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /src/api
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
WORKDIR /src
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
HEALTHCHECK --interval=5s --timeout=5s --retries=5 CMD curl --include --request GET http://localhost:8000/healthcheck || exit 1
```

### Backend Dockerfile
Similar structure for Celery worker container.

## Key Technologies

- **FastAPI**: Modern Python web framework
- **SQLModel**: SQLAlchemy-based ORM with Pydantic integration
- **Celery**: Distributed task queue
- **RabbitMQ**: Message broker
- **MinIO**: S3-compatible object storage
- **PostgreSQL**: Relational database
- **Docker Compose**: Container orchestration
- **uv**: Modern Python package manager
- **Ruff**: Fast Python linter and formatter
- **pytest**: Testing framework
- **MkDocs**: Documentation generator

## Development Best Practices

1. **Always run `make checks`** before committing
2. **Use `uv add`** for adding new dependencies
3. **Follow NumPy docstring format** for documentation
4. **Write tests** for new functionality
5. **Use type hints** throughout the codebase
6. **Run pre-commit hooks** to maintain code quality
7. **Keep requirements.txt in sync** with pyproject.toml dependencies
