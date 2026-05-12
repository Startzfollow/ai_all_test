## Business Dataset Acceptance

The platform includes a deterministic field-service demo dataset for business-level acceptance testing.

```bash
python scripts/create_field_service_demo_dataset.py --overwrite
PYTHONPATH=. python scripts/run_business_dataset_acceptance.py --with-business-smoke --with-quality-eval
```

This validates RAG documents, YOLO label structure, LLaVA/VQA samples, GUI Agent task samples, Business Platform V3 smoke tests, and quality evaluation gates.
