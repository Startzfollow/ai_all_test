from typing import List

from backend.app.rag.chunker import TextChunker


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 80) -> List[str]:
    return [chunk.text for chunk in TextChunker(chunk_size, chunk_overlap).split_text(text)]
