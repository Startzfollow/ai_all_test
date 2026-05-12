from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.app.rag.embeddings import EmbeddingBackend
from backend.app.rag.types import RetrievalHit
from backend.app.rag.vector_store import VectorStore


class Retriever:
    """Embed query and retrieve top-k chunks from a vector store."""

    def __init__(self, embedding: EmbeddingBackend, store: VectorStore):
        self.embedding = embedding
        self.store = store

    def retrieve(
        self,
        question: str,
        top_k: int = 4,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalHit]:
        vector = self.embedding.encode([question])[0]
        return self.store.search(vector, top_k=top_k, filters=filters)
