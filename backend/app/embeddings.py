# app/embeddings.py
from functools import lru_cache

from langchain_ollama import OllamaEmbeddings

from app.config import EMBEDDING_MODEL, OLLAMA_BASE_URL


@lru_cache
def get_embeddings_client() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)


async def embed_text(text: str) -> list[float]:
    return await get_embeddings_client().aembed_query(text)
