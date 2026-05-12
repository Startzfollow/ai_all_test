# Screenshot Evidence Guide

Screenshots make the repository look verifiable. Add at least these three files:

```text
docs/assets/api_docs.png
docs/assets/frontend_dashboard.png
docs/assets/gui_agent_trace.png
```

## 1. Start backend

```bash
python scripts/ingest_sample_docs.py
bash scripts/run_backend.sh
```

Open:

```text
http://127.0.0.1:8000/docs
```

Capture `docs/assets/api_docs.png`.

## 2. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Capture `docs/assets/frontend_dashboard.png`.

## 3. Capture GUI Agent trace

In the frontend, switch to **GUI Agent Planner**, click **生成动作计划**, then capture:

```text
docs/assets/gui_agent_trace.png
```

## Optional automatic capture

```bash
pip install playwright
python -m playwright install chromium
python scripts/capture_demo_screenshots.py
```

After screenshots are created, add this to README:

```markdown
## Demo Screenshots

![Backend API Docs](docs/assets/api_docs.png)
![Frontend Dashboard](docs/assets/frontend_dashboard.png)
![GUI Agent Trace](docs/assets/gui_agent_trace.png)
```
