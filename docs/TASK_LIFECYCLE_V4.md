# Task Lifecycle V4

## Why this matters

RAG indexing, YOLO benchmarking, LLaVA training and report generation are not simple request-response actions. They are business tasks that need traceability.

## Lifecycle

```text
pending -> running -> succeeded
pending -> running -> failed
pending -> cancelled
running -> timeout
```

## Required Task Fields

- task_id
- task_type
- project_id
- payload
- status
- progress
- priority
- retry_count
- max_retries
- started_at
- finished_at
- error_message
- result_uri
- log_uri

## Acceptance

```bash
PYTHONPATH=. python scripts/task_lifecycle_smoke_v4.py
```

Expected checks:

- create task
- run task
- write logs
- write events
- save result URI
- cancel pending task
- fail unknown task safely
