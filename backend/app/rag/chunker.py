from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from backend.app.rag.types import DocumentChunk

SUPPORTED_SUFFIXES = {".txt", ".md", ".csv", ".json"}


class TextChunker:
    """Deterministic offline text chunker.

    This implementation is intentionally dependency-free so the demo is runnable
    in CI and on a fresh machine. It uses paragraph-aware packing with overlap.
    For a production knowledge base, replace this with markdown/header-aware
    or semantic chunking while keeping the same public interface.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str, source: str = "") -> List[DocumentChunk]:
        normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if not normalized:
            return []

        chunks: List[DocumentChunk] = []
        start = 0
        idx = 0
        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            chunk_text = normalized[start:end].strip()
            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        text=chunk_text,
                        metadata={"source": source, "chunk_id": idx, "chunk_size": len(chunk_text)},
                    )
                )
                idx += 1
            if end == len(normalized):
                break
            start = max(0, end - self.chunk_overlap)
        return chunks

    def split_documents(self, paths: Iterable[Path]) -> List[DocumentChunk]:
        all_chunks: List[DocumentChunk] = []
        for path in paths:
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            all_chunks.extend(self.split_text(content, source=str(path)))
        return all_chunks
