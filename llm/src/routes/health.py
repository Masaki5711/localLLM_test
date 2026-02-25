import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_host}/")
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    return JSONResponse(
        content={
            "status": "healthy" if ollama_ok else "degraded",
            "service": "llm-service",
            "version": "0.1.0",
            "ollama": "connected" if ollama_ok else "disconnected",
            "model": settings.llm_model,
        }
    )
