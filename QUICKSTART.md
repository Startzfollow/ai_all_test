# Quickstart

## Minimal backend demo

```bash
cp .env.example .env 2>/dev/null || true
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/ingest_sample_docs.py
pytest -q
bash scripts/run_backend.sh
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Frontend demo

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Evidence generation

```bash
python scripts/eval_rag.py --documents-dir examples/docs --top-k 4
python scripts/benchmark_yolo.py --model weights/yolov8n.pt --image examples/images/demo.png --runs 30
python scripts/capture_demo_screenshots.py
```

The YOLO benchmark requires a real model file and `ultralytics`. If missing, the script exits with a clear error instead of generating fake numbers.
