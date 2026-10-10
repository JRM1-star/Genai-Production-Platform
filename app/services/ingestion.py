import hashlib
import io
from pathlib import Path
from pypdf import PdfReader

ALLOWED_TYPES = {"application/pdf", "text/plain", "text/markdown"}
MAX_CHUNK_CHARS = 1800
OVERLAP_CHARS = 250

def extract_text(filename: str, content_type: str, data: bytes) -> str:
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return data.decode("utf-8", errors="replace")

def chunk_text(text: str) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + MAX_CHUNK_CHARS, len(normalized))
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(normalized):
            break
        start = max(end - OVERLAP_CHARS, start + 1)
    return chunks

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def validate_upload(filename: str, content_type: str, data: bytes, max_bytes: int) -> None:
    if len(data) > max_bytes:
        raise ValueError(f"File exceeds the {max_bytes // (1024 * 1024)} MB limit")
    suffix = Path(filename).suffix.lower()
    if content_type not in ALLOWED_TYPES and suffix not in {".pdf", ".txt", ".md"}:
        raise ValueError("Unsupported file type. Use PDF, TXT or Markdown.")
