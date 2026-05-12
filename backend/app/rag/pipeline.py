from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.core.config import get_settings
from backend.app.rag.chunker import SUPPORTED_SUFFIXES, TextChunker
from backend.app.rag.embeddings import build_embedding
from backend.app.rag.local_store import LocalJsonVectorStore
from backend.app.rag.qdrant_store import QdrantVectorStore
from backend.app.rag.reranker import SimpleReranker
from backend.app.rag.retriever import Retriever
from backend.app.rag.types import RetrievalHit
from backend.app.schemas import RagQueryResponse, RagSource


class RagPipeline:
    """End-to-end RAG pipeline with explicit layers."""

    def __init__(self):
        self.settings = get_settings()
        rag_cfg = self.settings.rag
        self.chunker = TextChunker(
            chunk_size=int(rag_cfg.get("chunk_size", 500)),
            chunk_overlap=int(rag_cfg.get("chunk_overlap", 80)),
        )
        self.embedding = build_embedding(rag_cfg.get("embedding_model_path", ""))
        self.store = self._build_store()
        self.retriever = Retriever(self.embedding, self.store)
        self.reranker = SimpleReranker()

    def _build_store(self):
        rag_cfg = self.settings.rag
        backend = rag_cfg.get("vector_backend", "local")
        if backend == "qdrant":
            try:
                return QdrantVectorStore(
                    url=rag_cfg.get("qdrant_url", "http://127.0.0.1:6333"),
                    collection=rag_cfg.get("qdrant_collection", "ai_fullstack_docs"),
                    dim=self.embedding.dim,
                )
            except Exception:
                # Keep the demo available even when qdrant is not running.
                pass
        return LocalJsonVectorStore(rag_cfg.get("local_store_path", "vector_db/local_rag_store.json"))

    def ingest_dir(self, documents_dir: str, collection: Optional[str] = None) -> Dict[str, Any]:
        directory = Path(documents_dir)
        if not directory.exists():
            return {"ok": False, "message": f"documents_dir not found: {documents_dir}", "count": 0}

        paths = [path for path in directory.rglob("*") if path.suffix.lower() in SUPPORTED_SUFFIXES]
        chunks = self.chunker.split_documents(paths)
        if not chunks:
            return {"ok": False, "message": "no supported documents found", "count": 0}

        texts = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        vectors = self.embedding.encode(texts)
        count = self.store.upsert(texts, vectors, metadatas)
        return {
            "ok": True,
            "message": "ingested",
            "count": count,
            "documents_dir": str(directory),
            "vector_backend": self.settings.rag.get("vector_backend", "local"),
        }

    def retrieve(self, question: str, top_k: int = 4) -> List[RetrievalHit]:
        hits = self.retriever.retrieve(question, top_k=top_k)
        return self.reranker.rerank(question, hits)

    def query(self, question: str, top_k: int = 4, collection: Optional[str] = None) -> RagQueryResponse:
        hits = self.retrieve(question, top_k=top_k)
        context = "\n\n".join(f"[{idx + 1}] {hit.text}" for idx, hit in enumerate(hits))
        answer = self._generate_answer(question, context)
        return RagQueryResponse(
            answer=answer,
            sources=[
                RagSource(
                    doc_id=hit.id,
                    score=float(hit.score),
                    text=hit.text,
                    metadata=hit.metadata,
                )
                for hit in hits
            ],
        )

    def _generate_answer(self, question: str, context: str) -> str:
        llm_cfg = self.settings.llm
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=llm_cfg.get("api_key", "EMPTY"),
                base_url=llm_cfg.get("openai_base_url"),
            )
            resp = client.chat.completions.create(
                model=llm_cfg.get("model", "qwen-local"),
                temperature=float(llm_cfg.get("temperature", 0.2)),
                messages=[
                    {"role": "system", "content": "你是一个严谨的 RAG 问答助手，只根据给定上下文回答。"},
                    {"role": "user", "content": f"问题：{question}\n\n上下文：\n{context}"},
                ],
            )
            return resp.choices[0].message.content or ""
        except Exception:
            if context.strip():
                return (
                    "根据已检索到的资料，和问题最相关的内容如下：\n\n"
                    f"{context}\n\n"
                    "当前为离线 fallback 生成。接入本地 LLM 后可替换为自然语言综合答案。"
                )
            return "未检索到相关内容。请先调用 /api/rag/ingest 导入文档，或检查向量库配置。"
