from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model_name,
        encode_kwargs={"normalize_embeddings": True},
    )
