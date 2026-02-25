"""Main ETL processing pipeline."""
import logging
from uuid import uuid4

from src.services.parser import parse_document
from src.services.chunker import chunk_text
from src.services import embedding, qdrant_client, minio_client

logger = logging.getLogger(__name__)


async def process_document(
    file_bytes: bytes,
    file_name: str,
    document_type: str = "",
    department: str = "",
) -> dict[str, str | int]:
    """Full ETL pipeline for a document.
    
    Steps:
    1. Upload to MinIO
    2. Parse document
    3. Chunk text
    4. Generate embeddings
    5. Store in Qdrant
    """
    document_id = str(uuid4())
    ext = file_name.rsplit(".", 1)[-1].lower()

    content_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    # Step 1: Upload to MinIO
    object_key = f"{document_id}/{file_name}"
    minio_client.upload_file(
        object_key, file_bytes, content_types.get(ext, "application/octet-stream")
    )
    logger.info("[%s] Uploaded to MinIO: %s", document_id, object_key)

    # Step 2: Parse document
    parsed = parse_document(file_bytes, file_name)
    logger.info(
        "[%s] Parsed: %d pages, %d chars",
        document_id, len(parsed.pages), len(parsed.text),
    )

    # Step 3: Chunk text
    chunks = chunk_text(parsed.text)
    logger.info("[%s] Chunked into %d chunks", document_id, len(chunks))

    if not chunks:
        return {
            "document_id": document_id,
            "status": "completed",
            "chunk_count": 0,
            "minio_object_key": object_key,
        }

    # Step 4: Generate embeddings
    texts = [c["text"] for c in chunks]
    # Process in batches of 8
    all_embeddings: list[dict] = []
    batch_size = 8
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_embeddings = await embedding.generate_embeddings(batch)
        all_embeddings.extend(batch_embeddings)

    logger.info("[%s] Generated %d embeddings", document_id, len(all_embeddings))

    # Step 5: Store in Qdrant
    metadata = {
        "file_name": file_name,
        "file_type": ext,
        "document_type": document_type,
        "department": department,
    }
    count = await qdrant_client.upsert_chunks(
        document_id, chunks, all_embeddings, metadata
    )
    logger.info("[%s] Stored %d chunks in Qdrant", document_id, count)

    return {
        "document_id": document_id,
        "status": "completed",
        "chunk_count": count,
        "minio_object_key": object_key,
    }
