.PHONY: setup qdrant ingest backend frontend test lint quality rag-eval clean ci zip

setup:
	pip install -r requirements.txt

qdrant:
	docker compose up -d qdrant

ingest:
	python scripts/ingest_sample_docs.py

backend:
	bash scripts/run_backend.sh

frontend:
	cd frontend && npm install && npm run dev

test:
	pytest -q

lint:
	ruff check backend scripts || true
	ruff format --check backend scripts || true

quality:
	bash scripts/check_repo_quality.sh

rag-eval:
	python scripts/eval_rag.py --documents-dir examples/docs --top-k 4

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache backend/.pytest_cache output outputs logs
	find . -name "*.pyc" -delete

ci: test quality

rag-eval:
	python scripts/eval_rag.py --documents-dir examples/docs --top-k 4

yolo-bench:
	python scripts/benchmark_yolo.py --model weights/yolov8n.pt --image examples/images/demo.png --runs 30

screenshots:
	python scripts/capture_demo_screenshots.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache frontend/dist output

flatten:
	bash scripts/flatten_repository.sh

zip:
	cd .. && zip -r ai-fullstack-multimodal-agent-suite.zip ai-fullstack-multimodal-agent-suite -x "*/.git/*" "*/node_modules/*" "*/__pycache__/*" "*.pt" "*.onnx" "*.engine"
