"""Client for LLM Service embedding API."""
import logging
from typing import Any

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


async def generate_embeddings(texts: list[str]) -> list[dict[str, Any]]:
    """Generate embeddings via LLM Service."""
    if not texts:
        return []

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{settings.llm_service_url}/internal/embeddings",
            json={"texts": texts, "return_sparse": True},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("embeddings", [])
