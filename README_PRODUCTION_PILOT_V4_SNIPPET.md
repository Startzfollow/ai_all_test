## Production Pilot V4

This repository includes a Production Pilot V4 layer for field-service AI operations:

- task lifecycle with logs, events, result URI and cancellation
- object store smoke validation
- database health validation
- customer-facing pilot report generation
- prod-lite Docker Compose for PostgreSQL, MinIO and Qdrant
- CI workflow for production-pilot acceptance

Run:

```bash
PYTHONPATH=. python scripts/production_pilot_v4_acceptance.py
```

Expected output:

```text
outputs/production_pilot_v4/production_pilot_v4_acceptance.json
outputs/production_pilot_v4/production_pilot_v4_acceptance.md
```
