from functools import lru_cache

import torch
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings
from app.features.workspace.core.constants import EMBEDDING_MODEL_NAME


def _embedding_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    model_kwargs: dict[str, str] = {"device": _embedding_device()}
    if settings.hf_token:
        model_kwargs["token"] = settings.hf_token

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs={"normalize_embeddings": True},
    )
