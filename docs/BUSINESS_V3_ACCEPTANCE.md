# Business V3 Acceptance

## Run locally with SQLite

```bash
python scripts/init_business_db.py
python scripts/seed_business_demo.py
python scripts/business_platform_smoke.py
```

## Run with PostgreSQL

```bash
docker compose -f docker-compose.business.yml up -d postgres minio qdrant
export BUSINESS_DB_URL=postgresql://postgres:postgres@localhost:5432/ai_ops
export BUSINESS_OBJECT_STORE_ROOT=outputs/object_store
pip install -r requirements-business.txt
python scripts/init_business_db.py
python scripts/seed_business_demo.py
python scripts/business_platform_smoke.py
```

## Acceptance Criteria

| Gate | Target |
|---|---|
| Business API status | pass |
| Project creation | pass |
| Asset storage | pass |
| RAG task | pass or graceful failure with evidence |
| YOLO task | pass when weights/image exist |
| LLaVA train task | planned without accidental long run |
| Report generation | pass |
| Evaluation persistence | pass |
| GPU monitoring | pass if nvidia-smi available |
