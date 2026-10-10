from datetime import datetime

from pydantic import BaseModel, Field


class Source(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    score: float
    excerpt: str

class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    grounded: bool
    request_id: str

class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    chunk_count: int
    created_at: datetime

class HealthResponse(BaseModel):
    status: str
    version: str
