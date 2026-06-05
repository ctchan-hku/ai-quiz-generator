import shutil
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.features.workspace.core.embedder import get_embedding_model


class FaissIndexStore:
    def __init__(self, index_dir: Path, index_name: str = "index") -> None:
        self._index_dir = index_dir
        self._index_name = index_name

    def exists(self) -> bool:
        directory = self._index_dir
        return (directory / f"{self._index_name}.faiss").exists() and (
            directory / f"{self._index_name}.pkl"
        ).exists()

    def save(self, documents: list[Document]) -> None:
        directory = self._index_dir
        directory.mkdir(parents=True, exist_ok=True)
        embeddings = get_embedding_model()
        store = FAISS.from_documents(documents, embeddings)
        store.save_local(str(directory), index_name=self._index_name)

    def load(self) -> FAISS | None:
        if not self.exists():
            return None
        embeddings = get_embedding_model()
        return FAISS.load_local(
            str(self._index_dir),
            embeddings,
            index_name=self._index_name,
            allow_dangerous_deserialization=True,
        )

    def add(self, documents: list[Document]) -> None:
        store = self.load()
        if store is None:
            self.save(documents)
            return
        store.add_documents(documents)
        directory = self._index_dir
        directory.mkdir(parents=True, exist_ok=True)
        store.save_local(str(directory), index_name=self._index_name)

    def delete(self) -> None:
        if self._index_dir.exists():
            shutil.rmtree(self._index_dir)
