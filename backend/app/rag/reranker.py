from __future__ import annotations

from typing import List

from backend.app.rag.types import RetrievalHit


class SimpleReranker:
    """Optional reranking hook.

    The current implementation keeps vector-search order. The interface exists
    so a BGE reranker, cross-encoder, or LLM-based reranker can be plugged in
    without changing API handlers.
    """

    def rerank(self, question: str, hits: List[RetrievalHit]) -> List[RetrievalHit]:
        return hits
