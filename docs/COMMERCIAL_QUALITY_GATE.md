# Commercial Quality Gate

This checklist defines when the project can be called a demo, a commercial PoC, a pilot candidate or a production candidate.

## Level 1: Technical Demo

Required:

- Product smoke acceptance passes.
- Backend API starts.
- RAG, GUI Agent, VLM/LLaVA and YOLO routes are callable.
- CI workflow is green.
- Large weights and private datasets are excluded from Git.

Allowed wording:

> The project is a runnable AI engineering demo with product smoke acceptance.

## Level 2: Commercial PoC

Required:

- Product smoke acceptance passes.
- Quality score is at least 0.65.
- RAG has a small QA evaluation set and recall/source metrics.
- YOLO has real benchmark evidence and either accuracy metrics or a documented validation plan.
- LLaVA has data validation, training configuration and at least a smoke-training evidence record.
- GUI Agent has task cases, forbidden-action rules and trace output.

Allowed wording:

> The project is suitable for a scoped commercial proof of concept under controlled assumptions.

## Level 3: Pilot Release Candidate

Required:

- Quality score is at least 0.80.
- RAG achieves target recall and citation coverage on a business dataset.
- YOLO reports Precision, Recall, mAP50 and latency on business images.
- LLaVA reports baseline vs fine-tuned evaluation results.
- GUI Agent task success rate is measured and unsafe action rate is zero.
- Observability, logs, API keys, error handling and backup/rollback procedures exist.

Allowed wording:

> The project is ready for a limited pilot with monitoring and human supervision.

## Level 4: Production Candidate

Required:

- Quality score is at least 0.90.
- Security review passed.
- Monitoring and alerting are configured.
- Rate limits, authentication and audit logs are implemented.
- Data retention and privacy policy are defined.
- Rollback plan and SLA are documented.
- Real user acceptance testing is completed.

Allowed wording:

> The system is a production candidate pending organizational approval.

## Forbidden Claims Without Evidence

Do not claim:

- "production-ready" without monitoring, auth, rollback and security review;
- "high accuracy" without metrics;
- "completed large-scale LLaVA training" without logs, metrics and model evidence;
- "commercial deployment" without deployment, observability and support plan.
