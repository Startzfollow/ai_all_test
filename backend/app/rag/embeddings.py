from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Iterable, List, Protocol

import numpy as np


class EmbeddingBackend(Protocol):
    dim: int

    def encode(self, texts: Iterable[str]) -> List[List[float]]:
        ...


class HashingEmbedding:
    """Offline deterministic embedding used for CI and mini demos.

    It is not intended to match real semantic embeddings. Its job is to keep
    the pipeline runnable without downloading a model. For real experiments,
    set the embedding path to a local BGE/m3e/Qwen embedding model.
    """

    def __init__(self, dim: int = 384):
        self.dim = dim

    def encode(self, texts: Iterable[str]) -> List[List[float]]:
        return [self._hash_embed(text) for text in texts]

    def _hash_embed(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = self._tokenize(text)
        if not tokens:
            tokens = [text]
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            idx = int(digest[:8], 16) % self.dim
            sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec /= norm
        return vec.tolist()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        tokens: List[str] = []
        buff: List[str] = []
        for ch in text.lower():
            if "\u4e00" <= ch <= "\u9fff":
                if buff:
                    tokens.append("".join(buff))
                    buff = []
                tokens.append(ch)
            elif ch.isalnum() or ch in {"_", "-"}:
                buff.append(ch)
            else:
                if buff:
                    tokens.append("".join(buff))
                    buff = []
        if buff:
            tokens.append("".join(buff))
        cjk_chars = [t for t in tokens if len(t) == 1 and "\u4e00" <= t <= "\u9fff"]
        tokens.extend("".join(pair) for pair in zip(cjk_chars, cjk_chars[1:]))
        return tokens


class SentenceTransformerEmbedding:
    """Sentence-Transformers wrapper for local embedding models."""

    def __init__(self, model_path: str):
        if not model_path or not Path(model_path).exists():
            raise FileNotFoundError(f"embedding model path not found: {model_path}")
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_path)
        self.dim = int(self.model.get_sentence_embedding_dimension())

    def encode(self, texts: Iterable[str]) -> List[List[float]]:
        vectors = self.model.encode(list(texts), normalize_embeddings=True)
        return vectors.tolist()


def build_embedding(model_path: str = "", dim: int = 384) -> EmbeddingBackend:
    if model_path and Path(model_path).exists():
        try:
            return SentenceTransformerEmbedding(model_path)
        except Exception:
            # CI/demo fallback. Do not fail the whole application because an
            # optional local embedding model is missing dependencies.
            pass
    return HashingEmbedding(dim=dim)


def cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
