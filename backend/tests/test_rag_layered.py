from pathlib import Path

from backend.app.rag.chunker import TextChunker
from backend.app.rag.embeddings import HashingEmbedding
from backend.app.rag.local_store import LocalJsonVectorStore
from backend.app.rag.retriever import Retriever


def test_chunker_produces_metadata():
    chunker = TextChunker(chunk_size=20, chunk_overlap=5)
    chunks = chunker.split_text("RAG 知识库问答支持向量检索和上下文生成。", source="demo.md")
    assert chunks
    assert chunks[0].metadata["source"] == "demo.md"
    assert "chunk_id" in chunks[0].metadata


def test_local_store_retriever_roundtrip(tmp_path: Path):
    embedding = HashingEmbedding(dim=64)
    store = LocalJsonVectorStore(str(tmp_path / "store.json"))
    texts = ["RAG 使用向量数据库进行相似度检索", "YOLO 支持本地推理和加速"]
    store.upsert(texts, embedding.encode(texts), [{"source": "a"}, {"source": "b"}])
    hits = Retriever(embedding, store).retrieve("向量数据库", top_k=1)
    assert len(hits) == 1
    assert hits[0].text
