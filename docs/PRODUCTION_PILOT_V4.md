# Production Pilot V4 Upgrade

This upgrade moves the project from a business PoC toward a production-pilot candidate.

## Goals

- Production-style task lifecycle
- Per-task logs, events, result URI, error handling, cancellation
- Object storage validation
- Database health validation
- Customer-facing pilot report generation
- Prod-lite deployment assets
- Acceptance report for pilot readiness

## New Commands

```bash
PYTHONPATH=. python scripts/task_lifecycle_smoke_v4.py
PYTHONPATH=. python scripts/object_store_smoke_v4.py
PYTHONPATH=. python scripts/db_health_check_v4.py
PYTHONPATH=. python scripts/generate_customer_business_report_v4.py
PYTHONPATH=. python scripts/production_pilot_v4_acceptance.py
```

## Release Interpretation

| Level | Meaning |
|---|---|
| commercial_poc | Business flow is demonstrable |
| pilot_candidate | Business dataset acceptance and quality checks pass |
| production_pilot_candidate | Task lifecycle, object storage, database health, business acceptance and customer report pass |

## What This Does Not Claim

This is not yet a fully managed multi-tenant SaaS. It is a single-workspace, production-pilot-oriented AI platform prototype.
