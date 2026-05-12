# V4 Acceptance Guide

## One-command V4 acceptance

```bash
PYTHONPATH=. python scripts/production_pilot_v4_acceptance.py
```

## Expected Outputs

```text
outputs/production_pilot_v4/production_pilot_v4_acceptance.json
outputs/production_pilot_v4/production_pilot_v4_acceptance.md
outputs/reports_v4/field_service_customer_report.md
```

## Gate

A production-pilot candidate should pass:

- task lifecycle smoke
- object store smoke
- database health check
- business dataset acceptance
- customer report generation

## Recommended next hardening

1. Replace the JSON task store with PostgreSQL repository methods.
2. Replace local object store fallback with MinIO/S3 adapter.
3. Add task log streaming to the frontend.
4. Add true async worker concurrency and retry policies.
5. Add measured RAG / YOLO / VQA quality metrics.
