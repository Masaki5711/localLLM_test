"""Document management routes."""
import logging
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from src.services import pipeline, qdrant_client, minio_client

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(""),
    department: str = Form(""),
) -> JSONResponse:
    """Upload and process a document."""
    file_name = file.filename or "unknown"
    file_ext = "." + file_name.rsplit(".", 1)[-1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {ALLOWED_EXTENSIONS}",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 100MB.")

    try:
        result = await pipeline.process_document(
            file_bytes, file_name, document_type, department
        )
    except Exception as e:
        logger.exception("ETL pipeline failed for %s", file_name)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    return JSONResponse(
        status_code=202,
        content={
            "success": True,
            "data": {
                "document_id": result["document_id"],
                "status": result["status"],
                "chunk_count": result["chunk_count"],
                "message": f"Document '{file_name}' processed successfully",
            },
        },
    )


@router.get("/documents")
async def list_documents() -> JSONResponse:
    """List all documents (placeholder)."""
    return JSONResponse(
        content={
            "success": True,
            "data": [],
            "meta": {"total": 0, "page": 1, "limit": 20},
        }
    )


@router.post("/search")
async def search_documents(request: dict) -> JSONResponse:  # type: ignore[type-arg]
    """Search documents using vector similarity."""
    from src.services import embedding as emb_service

    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    limit = request.get("limit", 10)
    filters = request.get("filters", {})

    # Generate query embedding
    query_embeddings = await emb_service.generate_embeddings([query])
    if not query_embeddings:
        raise HTTPException(status_code=500, detail="Failed to generate query embedding")

    query_vector = query_embeddings[0].get("dense", [])

    # Search Qdrant
    search_filters = {"is_latest": True}
    if filters.get("document_type"):
        search_filters["document_type"] = filters["document_type"]
    if filters.get("department"):
        search_filters["department"] = filters["department"]

    results = await qdrant_client.search_chunks(
        query_vector=query_vector, limit=limit, filters=search_filters
    )

    return JSONResponse(
        content={
            "success": True,
            "data": {"results": results, "total": len(results)},
        }
    )
