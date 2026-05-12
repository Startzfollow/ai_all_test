# Demo Results

This directory contains execution results and screenshots from running the project.

## Screenshots

Place your screenshots here:

- `api_docs.png` - FastAPI documentation page (`/docs`)
- `frontend_demo.png` - React dashboard running
- `mini_demo_output.png` - Output from running `python scripts/run_mini_demo.py`
- `yolo_benchmark.png` - YOLO inference results
- `rag_query.png` - RAG query results

## How to Capture Screenshots

1. Start the backend server:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```

2. Open browser to http://localhost:8000/docs

3. Capture screenshots and save to this directory

4. Update README.md to reference these screenshots