import asyncio
import logging
import os
import tempfile

from celery import Celery
from minio import Minio
from sqlmodel import Session, create_engine

from api.core import embeddings, models
from api.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery("tasks", broker="amqp://guest:guest@rabbitmq:5672", backend="rpc://")

# Configure Celery logging
app.conf.update(
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(task_name)s[%(task_id)s]: %(message)s",
)

# Database setup for backend
DB_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
engine = create_engine(DB_URL)

# MinIO client setup
minio_client = Minio(
    f"{settings.minio_host}:9000",
    access_key=settings.minio_root_user,
    secret_key=settings.minio_root_password,
    secure=False,
)
BUCKET = "images"


@app.task(name="process_file")
def process_file(user_id: int, filename: str, content_type: str) -> str:
    """
    Process an uploaded file: generate embeddings and store metadata.

    Parameters
    ----------
    user_id : int
        The ID of the user who uploaded the file.
    filename : str
        The name of the uploaded file.
    content_type : str
        The MIME type of the file.

    Returns
    -------
    str
        A confirmation message indicating successful processing.

    """
    try:
        # Construct MinIO path
        minio_path = f"{user_id}/{filename}"

        # Download file from MinIO to temporary location
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as temp_file:
            temp_path = temp_file.name
            try:
                # Get file from MinIO
                response = minio_client.get_object(BUCKET, minio_path)
                temp_file.write(response.read().decode("utf-8"))
                temp_file.flush()

                # Generate embedding from file content using OpenRouter API
                embedding = asyncio.run(embeddings.generate_embedding_from_file(temp_path))

                # Get file size from MinIO
                stat = minio_client.stat_object(BUCKET, minio_path)
                file_size = stat.size

                # Store metadata in database
                with Session(engine) as session:
                    file_metadata = models.FileMetadata(
                        user_id=user_id,
                        filename=filename,
                        content_type=content_type,
                        size=file_size,
                        minio_path=minio_path,
                        embedding=embedding,
                    )
                    session.add(file_metadata)
                    session.commit()

                return f"Successfully processed and embedded file '{filename}' for user {user_id}"

            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

    except Exception as e:
        # Log error and re-raise for Celery error handling
        logger.error(f"Error processing file {filename} for user {user_id}: {str(e)}")
        raise
