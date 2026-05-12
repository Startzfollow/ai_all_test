from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

from backend.app.rag.types import RetrievalHit


class VectorStore(Protocol):
    def upsert(
        self,
        texts: List[str],
        vectors: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        ...

    def search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalHit]:
        ...
