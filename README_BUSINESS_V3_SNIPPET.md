## Business Platform V3: Field Service Multimodal AI Copilot

This project now includes a business-oriented fullstack layer for field-service and equipment-maintenance workflows.

It provides:

- default single-workspace UI, no user system required;
- PostgreSQL-compatible data model for projects, assets, tasks, models, datasets, evaluations, and events;
- local object-storage adapter for images, PDFs, reports, model artifacts, and evaluation files;
- DB-backed task system for RAG indexing, YOLO benchmark, LLaVA training planning, and report generation;
- minimal monitoring for API health, GPU usage, task status, and failure events;
- business smoke test for acceptance.

Run:

```bash
python scripts/init_business_db.py
python scripts/seed_business_demo.py
python scripts/business_platform_smoke.py
```
