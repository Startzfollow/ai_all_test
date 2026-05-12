# Roadmap

## Done

- [x] FastAPI backend skeleton
- [x] React frontend demo dashboard
- [x] Local JSON vector store for dependency-light RAG demo
- [x] RAG ingest and query endpoint
- [x] GUI Agent dry-run planning endpoint
- [x] LLaVA-compatible multimodal endpoint wrapper
- [x] LLaVA-CoT style data preparation script
- [x] YOLO inference/export/benchmark script entrypoints
- [x] Docker Compose entry for Qdrant

## In Progress

- [ ] Add screenshots for backend docs and frontend dashboard
- [ ] Add measured YOLO benchmark JSON from local GPU machine
- [ ] Add Qdrant mode integration test
- [ ] Add real VLM backend adapter example
- [ ] Add LLaVA LoRA training dry-run log

## Next Milestones

1. Produce a reproducible RAG evaluation result with `scripts/eval_rag.py`.
2. Run YOLO benchmark on local GPU and commit only the JSON/Markdown result, not weight files.
3. Add frontend screenshots under `docs/assets/`.
4. Deploy backend and frontend demo to a public endpoint if required by the challenge.
