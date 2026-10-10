import uuid
from functools import lru_cache

from qdrant_client import QdrantClient, models

from app.core.config import get_settings
from app.services.embeddings import (
    embed_documents,
    embed_query,
    embedding_dimension,
)


@lru_cache
def get_qdrant() -> QdrantClient:
    settings = get_settings()
    kwargs = {"url": settings.qdrant_url}

    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key

    return QdrantClient(**kwargs)


def ensure_collection() -> None:
    client = get_qdrant()
    name = get_settings().qdrant_collection

    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(
                size=embedding_dimension(),
                distance=models.Distance.COSINE,
            ),
        )


def upsert_chunks(
    tenant_id: str,
    document_id: str,
    filename: str,
    chunks: list[str],
) -> None:
    client = get_qdrant()
    settings = get_settings()
    vectors = embed_documents(chunks)

    points = [
        models.PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{document_id}:{index}")),
            vector=vector,
            payload={
                "tenant_id": tenant_id,
                "document_id": document_id,
                "filename": filename,
                "chunk_id": str(index),
                "text": chunk,
            },
        )
        for index, (chunk, vector) in enumerate(zip(chunks, vectors,strict=True))
    ]

    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
        wait=True,
    )


def search(tenant_id: str, question: str, limit: int) -> list[dict]:
    client = get_qdrant()
    settings = get_settings()

    hits = client.query_points(
        collection_name=settings.qdrant_collection,
        query=embed_query(question),
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="tenant_id",
                    match=models.MatchValue(value=tenant_id),
                )
            ]
        ),
        with_payload=True,
        limit=limit,
    ).points

    return [
        {
            "document_id": str(hit.payload["document_id"]),
            "filename": str(hit.payload["filename"]),
            "chunk_id": str(hit.payload["chunk_id"]),
            "text": str(hit.payload["text"]),
            "score": float(hit.score),
        }
        for hit in hits
    ]