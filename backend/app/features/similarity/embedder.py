from functools import lru_cache

import torch
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings


def _embedding_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model_name,
        model_kwargs={"device": _embedding_device()},
        encode_kwargs={"normalize_embeddings": True},
    )
