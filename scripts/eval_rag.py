#!/usr/bin/env python3
"""Small, reproducible RAG evaluation script.

The goal is not to benchmark a production RAG system. It verifies that the local
RAG pipeline can ingest documents, retrieve relevant chunks and return sources.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.rag_service import RagService

DEFAULT_QUERIES = [
    "这个项目覆盖了哪些 AI 技术栈？",
    "RAG 模块使用了什么向量库？",
    "YOLO 模块支持哪些部署或加速方式？",
]


def evaluate(documents_dir: str, top_k: int) -> dict[str, Any]:
    service = RagService()
    ingest_result = service.ingest_dir(documents_dir)
    results = []

    for query in DEFAULT_QUERIES:
        response = service.query(query, top_k=top_k)
        results.append(
            {
                "query": query,
                "answer_preview": response.answer[:500],
                "source_count": len(response.sources),
                "top_sources": [
                    {
                        "score": round(source.score, 4),
                        "source": source.metadata.get("source"),
                        "text_preview": source.text[:180],
                    }
                    for source in response.sources
                ],
                "has_sources": bool(response.sources),
            }
        )

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "documents_dir": documents_dir,
        "top_k": top_k,
        "ingest": ingest_result,
        "queries": results,
        "passed": bool(ingest_result.get("ok")) and all(item["has_sources"] for item in results),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents-dir", default="examples/docs")
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    report = evaluate(args.documents_dir, args.top_k)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"rag_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nSaved RAG evaluation report to: {output_path}")

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
