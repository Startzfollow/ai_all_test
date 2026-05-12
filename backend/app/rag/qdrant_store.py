from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from backend.app.rag.types import RetrievalHit


class QdrantVectorStore:
    """Qdrant implementation for production-like RAG retrieval."""

    def __init__(self, url: str, collection: str, dim: int):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        self.client = QdrantClient(url=url)
        self.collection = collection
        existing = [item.name for item in self.client.get_collections().collections]
        if collection not in existing:
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(
        self,
        texts: List[str],
        vectors: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        from qdrant_client.models import PointStruct

        metadatas = metadatas or [{} for _ in texts]
        points = []
        for text, vector, metadata in zip(texts, vectors, metadatas):
            payload = dict(metadata)
            payload["text"] = text
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))
        self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalHit]:
        # TODO: translate filters into qdrant_client.models.Filter when needed.
        result = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
        )
        return [
            RetrievalHit(
                id=str(hit.id),
                score=float(hit.score),
                text=(hit.payload or {}).get("text", ""),
                metadata={k: v for k, v in (hit.payload or {}).items() if k != "text"},
            )
            for hit in result
        ]
