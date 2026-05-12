# API Reference

Base URL when running locally:

```text
http://127.0.0.1:8000
```

## System

### `GET /api/system/health`

Returns a minimal backend health result.

```json
{"ok": true, "service": "ai-fullstack-mm"}
```

### `GET /api/system/config`

Returns a redacted runtime configuration summary, including model paths, RAG backend and vision settings.

## RAG

### `POST /api/rag/ingest`

Ingests supported documents from a local directory.

Request:

```json
{"documents_dir": "examples/docs", "collection": "default"}
```

Response:

```json
{"ok": true, "message": "ingested", "count": 8}
```

### `POST /api/rag/query`

Runs retrieval over the local vector store or Qdrant backend and returns answer plus sources.

Request:

```json
{"question": "这个项目覆盖哪些 AI 技术栈？", "top_k": 4}
```

Response shape:

```json
{
  "answer": "...",
  "sources": [
    {"doc_id": "...", "score": 0.85, "text": "...", "metadata": {"source": "examples/docs/..."}}
  ]
}
```

## GUI Agent

### `POST /api/agent/gui/plan`

Converts a user task into a dry-run UI action plan.

Request:

```json
{"task": "打开知识库并查询 YOLO 推理加速方案", "dry_run": true}
```

The current implementation is intentionally dry-run first. It produces structured action JSON and avoids destructive UI operations.

## Multimodal / LLaVA-compatible VQA

### `POST /api/multimodal/llava/chat`

Request:

```json
{"image_path": "examples/images/chart.png", "prompt": "请解释图中的主要信息"}
```

This endpoint is designed as a service wrapper. It can be connected to a local LLaVA, Qwen-VL, vLLM, LMDeploy or OpenAI-compatible multimodal service.

## YOLO

### `POST /api/vision/yolo/infer`

Request:

```json
{"image_path": "examples/images/street.jpg", "model_path": "weights/yolov8n.pt", "confidence": 0.25, "image_size": 640}
```

If weights are missing, the endpoint should return a clear message rather than failing silently. This keeps the demo service robust on machines without local model files.
