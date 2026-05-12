# Product Acceptance Smoke Test

This document defines a small but product-oriented smoke test for the AI Fullstack Multimodal Agent Suite.

The goal is not to replace full unit tests, integration tests, or model evaluation. The goal is to provide a fast acceptance gate that answers:

1. Can the repository be accepted as a complete AI engineering project?
2. Do all major features have a minimal runnable path?
3. Are failures graceful when large models, Qdrant, TensorRT, or private datasets are unavailable?
4. Is the project clean enough to be published as a commercial-facing demo?

## Covered Capabilities

| Area | Smoke Coverage | Acceptance Meaning |
|---|---|---|
| Backend | FastAPI import, root endpoint, health endpoint, config endpoint | Service can start and expose product APIs |
| RAG | Ingest sample documents and query top-k sources | Knowledge-base flow is minimally usable |
| GUI Agent | Generate safe dry-run action plan | Agent planning works without destructive operations |
| LLaVA / VLM | Send image path and prompt to multimodal endpoint | VLM interface and fallback are usable |
| YOLO | Run detection endpoint or fail gracefully if model/runtime missing | Vision inference path has stable API behavior |
| RAG Evaluation | Execute `scripts/eval_rag.py` | Retrieval evaluation path is reproducible |
| LLaVA Training | Check experiment config, train script, metrics template, optional dataset validation | Training workflow is present and auditable |
| YOLO Benchmark | Check benchmark CLI, optional tiny benchmark run | Acceleration evaluation path is present |
| Frontend | Check React project assets, optional build | Product UI assets exist |
| Release Hygiene | Check CI, no secrets, no large model artifacts | Repository is suitable for public release |

## Run

Default offline smoke test:

```bash
python scripts/product_smoke_acceptance.py
```

Strict release gate:

```bash
python scripts/product_smoke_acceptance.py --strict
```

Optional checks:

```bash
python scripts/product_smoke_acceptance.py \
  --with-frontend \
  --with-yolo-benchmark \
  --with-llava-dataset data/processed/llava_cot_1k.jsonl
```

The script writes:

```text
outputs/smoke/product_smoke_report.json
outputs/smoke/product_smoke_report.md
```

## Acceptance Rules

Default mode accepts the project when:

- no critical check fails;
- score is at least 80;
- optional dependencies may be skipped.

Strict mode accepts the project when:

- no critical check fails;
- no check fails;
- score is at least 90.

## Product Release Interpretation

### Ready for competition submission

The repository is ready for competition submission when default smoke passes and CI is green.

### Ready for technical demo

The repository is ready for a live technical demo when:

- default smoke passes;
- frontend screenshots are present;
- RAG query returns sources;
- GUI Agent returns dry-run action plan;
- VLM and YOLO endpoints return stable schemas.

### Ready for commercial pilot

The repository is ready for commercial pilot only after:

- strict smoke passes;
- frontend build passes;
- at least one real LLaVA smoke training run has logs and metrics;
- YOLO benchmark has real latency data;
- release hygiene has no warnings;
- security/privacy review is completed;
- deployment variables are documented.