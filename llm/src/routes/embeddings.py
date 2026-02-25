import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import settings

router = APIRouter()


class EmbeddingRequest(BaseModel):
    texts: list[str]
    return_sparse: bool = False


class EmbeddingResponse(BaseModel):
    embeddings: list[dict[str, list[float] | dict[str, list[int | float]]]]


@router.post("/embeddings")
async def generate_embeddings(request: EmbeddingRequest) -> EmbeddingResponse:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.ollama_host}/api/embed",
                json={
                    "model": settings.embedding_model,
                    "input": request.texts,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings_list = data.get("embeddings", [])

            result = [{"dense": emb} for emb in embeddings_list]
            return EmbeddingResponse(embeddings=result)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {e}")
