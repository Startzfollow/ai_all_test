"""Layered RAG package.

This package separates RAG into ingestion, chunking, embedding, vector storage,
retrieval, optional reranking, and answer composition. The old
`backend.app.services.rag_service.RagService` is kept as a thin compatibility
wrapper around `RagPipeline`.
"""

from backend.app.rag.pipeline import RagPipeline

__all__ = ["RagPipeline"]
