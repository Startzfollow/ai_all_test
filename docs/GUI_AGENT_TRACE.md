# GUI Agent Trace Teaching Note

## Goal

A GUI Agent demo is stronger when it shows not only the final action list but also the reasoning trace:

```text
observe -> plan -> safety -> output
```

## Current design

- `backend/app/agent/action_schema.py` defines the action schema.
- `backend/app/agent/planner.py` creates a safe dry-run plan.
- `backend/app/agent/safety.py` marks risky actions for human review.
- `backend/app/agent/trace.py` records the trace timeline.

The API endpoint remains:

```http
POST /api/agent/gui/plan
```

The response now contains:

```json
{
  "task": "打开浏览器搜索 RAG",
  "plan": [{"action": "open_app", "target": "browser"}],
  "trace": [{"stage": "observe", "message": "received user task"}],
  "dry_run": true,
  "notes": "dry-run mode: actions are returned as JSON and not executed."
}
```

## Safety boundary

This repository should describe GUI Agent as **dry-run planning and structured action generation**. Do not claim that it safely controls arbitrary user desktops unless a real executor, permission model and sandbox are implemented.
