# PostgreSQL and MinIO Validation for V4

## Prod-lite Stack

```bash
docker compose -f docker-compose.prod-lite.yml up -d postgres minio qdrant
```

## PostgreSQL

```bash
export BUSINESS_DB_URL=postgresql://postgres:postgres@localhost:5432/ai_ops
PYTHONPATH=. python scripts/db_health_check_v4.py
```

The health check verifies connectivity and reports missing required tables. Table creation is still handled by the existing business DB initialization script.

## Object Storage

Default local mode:

```bash
PYTHONPATH=. python scripts/object_store_smoke_v4.py
```

For MinIO-backed deployments, keep the same object-store interface and replace the adapter behind it. The V4 smoke keeps a local fallback so CI stays lightweight.

## Required Object Types

- uploaded field images
- PDF / Markdown manuals
- RAG index artifacts
- YOLO benchmark JSON
- training evidence
- task logs
- customer reports
