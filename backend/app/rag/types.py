from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class DocumentChunk:
    """A chunk produced from a source document."""

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorRecord:
    """Stored vector record with text and metadata."""

    id: str
    text: str
    vector: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalHit:
    """Result returned by the retriever."""

    id: str
    text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
