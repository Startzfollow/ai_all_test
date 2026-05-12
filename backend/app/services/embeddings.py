from backend.app.rag.embeddings import HashingEmbedding, SentenceTransformerEmbedding, build_embedding, cosine


class EmbeddingModel:
    """Compatibility wrapper used by older imports."""

    def __init__(self, model_path: str = "", dim: int = 384):
        self.backend = build_embedding(model_path=model_path, dim=dim)
        self.dim = self.backend.dim

    def encode(self, texts):
        return self.backend.encode(texts)


__all__ = [
    "EmbeddingModel",
    "HashingEmbedding",
    "SentenceTransformerEmbedding",
    "build_embedding",
    "cosine",
]
