"""MinIO object storage client."""
import io
import logging

from minio import Minio

from src.config import settings

logger = logging.getLogger(__name__)


def get_minio_client() -> Minio:
    """Create MinIO client."""
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )


def ensure_bucket() -> None:
    """Create the documents bucket if it doesn't exist."""
    client = get_minio_client()
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)
        logger.info("Created bucket: %s", settings.minio_bucket)


def upload_file(object_key: str, file_bytes: bytes, content_type: str) -> str:
    """Upload a file to MinIO."""
    client = get_minio_client()
    client.put_object(
        settings.minio_bucket,
        object_key,
        io.BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=content_type,
    )
    logger.info("Uploaded %s to MinIO", object_key)
    return object_key


def download_file(object_key: str) -> bytes:
    """Download a file from MinIO."""
    client = get_minio_client()
    response = client.get_object(settings.minio_bucket, object_key)
    data = response.read()
    response.close()
    response.release_conn()
    return data
