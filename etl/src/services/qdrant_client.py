"""Qdrant vector database client."""
import logging
from typing import Any
from uuid import uuid4

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "document_chunks"


async def ensure_collection() -> None:
    """Create the document_chunks collection if it doesn't exist."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check if collection exists
        resp = await client.get(
            f"{settings.qdrant_url}/collections/{COLLECTION_NAME}"
        )
        if resp.status_code == 200:
            logger.info("Collection '%s' already exists", COLLECTION_NAME)
            return

        # Create collection with dense vector
        create_body = {
            "vectors": {
                "dense": {
                    "size": 1024,
                    "distance": "Cosine",
                }
            },
        }

        resp = await client.put(
            f"{settings.qdrant_url}/collections/{COLLECTION_NAME}",
            json=create_body,
        )
        resp.raise_for_status()
        logger.info("Created collection '%s'", COLLECTION_NAME)

        # Create payload indexes for filtering
        for field, schema in [
            ("document_type", {"type": "keyword"}),
            ("department", {"type": "keyword"}),
            ("file_type", {"type": "keyword"}),
            ("is_latest", {"type": "bool"}),
        ]:
            await client.put(
                f"{settings.qdrant_url}/collections/{COLLECTION_NAME}/index",
                json={"field_name": field, "field_schema": schema},
            )

        logger.info("Created payload indexes")


async def upsert_chunks(
    document_id: str,
    chunks: list[dict[str, Any]],
    embeddings: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> int:
    """Insert chunk vectors into Qdrant."""
    if not chunks or not embeddings:
        return 0

    points = []
    for chunk, embedding in zip(chunks, embeddings):
        point_id = str(uuid4())
        dense_vector = embedding.get("dense", [])

        payload = {
            "document_id": document_id,
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "heading": chunk.get("heading", ""),
            "char_count": chunk.get("char_count", 0),
            "file_name": metadata.get("file_name", ""),
            "file_type": metadata.get("file_type", ""),
            "document_type": metadata.get("document_type", ""),
            "department": metadata.get("department", ""),
            "is_latest": True,
        }

        points.append({
            "id": point_id,
            "vector": {"dense": dense_vector},
            "payload": payload,
        })

    # Batch upsert
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.put(
            f"{settings.qdrant_url}/collections/{COLLECTION_NAME}/points",
            json={"points": points},
        )
        resp.raise_for_status()

    logger.info("Upserted %d chunks for document %s", len(points), document_id)
    return len(points)


async def search_chunks(
    query_vector: list[float],
    limit: int = 10,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Search for similar chunks."""
    search_body: dict[str, Any] = {
        "vector": {"name": "dense", "vector": query_vector},
        "limit": limit,
        "with_payload": True,
    }

    if filters:
        must_conditions = []
        if "is_latest" in filters:
            must_conditions.append({
                "key": "is_latest",
                "match": {"value": filters["is_latest"]},
            })
        if "document_type" in filters:
            must_conditions.append({
                "key": "document_type",
                "match": {"any": filters["document_type"]},
            })
        if "department" in filters:
            must_conditions.append({
                "key": "department",
                "match": {"value": filters["department"]},
            })
        if must_conditions:
            search_body["filter"] = {"must": must_conditions}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.qdrant_url}/collections/{COLLECTION_NAME}/points/search",
            json=search_body,
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for point in data.get("result", []):
        payload = point.get("payload", {})
        results.append({
            "chunk_id": point.get("id"),
            "score": point.get("score", 0),
            "text": payload.get("text", ""),
            "document_id": payload.get("document_id", ""),
            "file_name": payload.get("file_name", ""),
            "heading": payload.get("heading", ""),
            "chunk_index": payload.get("chunk_index", 0),
        })

    return results


async def delete_document_chunks(document_id: str) -> None:
    """Delete all chunks for a document."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.qdrant_url}/collections/{COLLECTION_NAME}/points/delete",
            json={
                "filter": {
                    "must": [
                        {"key": "document_id", "match": {"value": document_id}}
                    ]
                }
            },
        )
        resp.raise_for_status()
    logger.info("Deleted chunks for document %s", document_id)
