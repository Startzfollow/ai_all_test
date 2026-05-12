from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.rag.embeddings import cosine
from backend.app.rag.types import RetrievalHit, VectorRecord


class LocalJsonVectorStore:
    """Tiny JSON vector store for reproducible local demos and CI.

    This is deliberately simple. It demonstrates vector-store semantics without
    requiring Qdrant/Milvus/Postgres. For large data, switch to Qdrant.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.records: List[VectorRecord] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.records = []
            return
        try:
            raw_records = json.loads(self.path.read_text(encoding="utf-8"))
            self.records = [VectorRecord(**record) for record in raw_records]
        except Exception:
            self.records = []

    def _save(self) -> None:
        payload = [record.__dict__ for record in self.records]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def upsert(
        self,
        texts: List[str],
        vectors: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        metadatas = metadatas or [{} for _ in texts]
        for text, vector, metadata in zip(texts, vectors, metadatas):
            self.records.append(
                VectorRecord(id=str(uuid.uuid4()), text=text, vector=vector, metadata=metadata)
            )
        self._save()
        return len(texts)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalHit]:
        filters = filters or {}
        hits: List[RetrievalHit] = []
        for record in self.records:
            if any(record.metadata.get(k) != v for k, v in filters.items()):
                continue
            hits.append(
                RetrievalHit(
                    id=record.id,
                    text=record.text,
                    score=cosine(query_vector, record.vector),
                    metadata=record.metadata,
                )
            )
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:top_k]
