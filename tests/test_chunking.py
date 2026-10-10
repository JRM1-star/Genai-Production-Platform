from app.services.ingestion import chunk_text, sha256_bytes

def test_chunking_has_overlap_and_content():
    text = "word " * 1000
    chunks = chunk_text(text)
    assert len(chunks) > 1
    assert all(chunks)
    assert chunks[0][-20:] in chunks[1]

def test_sha256_is_deterministic():
    assert sha256_bytes(b"hello") == sha256_bytes(b"hello")
    assert sha256_bytes(b"hello") != sha256_bytes(b"world")
