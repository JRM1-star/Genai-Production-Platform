import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authenticate
from app.core.config import get_settings
from app.domain.schemas import ChatRequest, ChatResponse, DocumentResponse, HealthResponse, Source
from app.graph.workflow import build_graph
from app.services.db import Document, document_exists, get_session
from app.services.ingestion import chunk_text, extract_text, sha256_bytes, validate_upload
from app.services.vector_store import ensure_collection, upsert_chunks

router = APIRouter()
graph = build_graph()

@router.get("/health/live", response_model=HealthResponse, tags=["health"])
async def live():
    s = get_settings()
    return HealthResponse(status="ok", version=s.app_version)

@router.get("/health/ready", response_model=HealthResponse, tags=["health"])
async def ready():
    ensure_collection()
    return HealthResponse(status="ready", version=get_settings().app_version)

@router.post("/v1/documents", response_model=DocumentResponse, tags=["documents"])
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
):
    settings = get_settings()
    data = await file.read()
    filename = file.filename or "unnamed"
    content_type = file.content_type or "application/octet-stream"

    try:
        validate_upload(filename, content_type, data, settings.max_upload_mb * 1024 * 1024)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    digest = sha256_bytes(data)
    if await document_exists(session, tenant_id, digest):
        raise HTTPException(status_code=409, detail="This document already exists for this tenant")

    chunks = chunk_text(extract_text(filename, content_type, data))
    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable text found")

    document_id = str(uuid.uuid4())
    record = Document(
        id=document_id,
        tenant_id=tenant_id,
        filename=filename,
        content_type=content_type,
        sha256=digest,
        chunk_count=len(chunks),
        created_at=datetime.now(timezone.utc),
    )
    session.add(record)
    await session.commit()

    try:
        ensure_collection()
        upsert_chunks(tenant_id, document_id, filename, chunks)
    except Exception as exc:
        await session.delete(record)
        await session.commit()
        raise HTTPException(status_code=503, detail="Vector indexing failed; document was not retained") from exc

    return DocumentResponse(
        id=document_id,
        filename=filename,
        content_type=content_type,
        chunk_count=len(chunks),
        created_at=record.created_at,
    )

@router.post("/v1/chat", response_model=ChatResponse, tags=["chat"])
async def chat(payload: ChatRequest, tenant_id: str = Depends(authenticate)):
    request_id = str(uuid.uuid4())
    result = await graph.ainvoke({"tenant_id": tenant_id, "question": payload.question})
    sources = [
        Source(
            document_id=item["document_id"],
            filename=item["filename"],
            chunk_id=item["chunk_id"],
            score=item["score"],
            excerpt=item["text"][:500],
        )
        for item in result.get("evidence", [])
    ]
    return ChatResponse(
        answer=result["answer"],
        sources=sources,
        grounded=result.get("grounded", False),
        request_id=request_id,
    )
