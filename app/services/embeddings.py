from functools import lru_cache
from fastembed import TextEmbedding
from app.core.config import get_settings

@lru_cache
def get_embedding_model() -> TextEmbedding:
    return TextEmbedding(model_name=get_settings().embedding_model)

def embed_documents(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return [vector.tolist() for vector in model.embed(texts)]

def embed_query(text: str) -> list[float]:
    model = get_embedding_model()
    return next(model.embed([text])).tolist()

def embedding_dimension() -> int:
    return len(embed_query("dimension probe"))
