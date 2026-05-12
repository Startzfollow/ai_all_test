# Commercial Release Checklist

This checklist upgrades the project from a competition demo to a commercial pilot candidate.

## 1. Acceptance Gates

- [ ] `python scripts/product_smoke_acceptance.py` passes.
- [ ] `python scripts/product_smoke_acceptance.py --strict` passes.
- [ ] GitHub Actions CI is green.
- [ ] `pytest -q backend/tests` passes.
- [ ] Frontend build passes.
- [ ] Docker backend image builds.
- [ ] Demo screenshots are present in `docs/assets`.

## 2. Model and Data Evidence

- [ ] LLaVA smoke training log is collected.
- [ ] LLaVA metrics JSON contains real values, not `None` or `TBD`.
- [ ] LLaVA inference examples are recorded.
- [ ] YOLO benchmark JSON contains measured latency and FPS.
- [ ] RAG evaluation JSON is generated.
- [ ] Model checkpoints and datasets are not committed to Git.

## 3. Product Quality

- [ ] All API errors return stable JSON, not stack traces.
- [ ] API schemas are documented.
- [ ] Demo UI clearly marks mock/fallback outputs.
- [ ] Long-running jobs have status reporting.
- [ ] Model paths and API keys are configured through environment variables.
- [ ] Logging is enabled and does not leak secrets.

## 4. Security and Privacy

- [ ] No API keys or private tokens in Git.
- [ ] No private datasets in Git.
- [ ] CORS is restricted for production.
- [ ] Upload size limits are defined.
- [ ] File path access is restricted.
- [ ] Destructive GUI Agent actions are disabled by default.
- [ ] User-uploaded images/documents have retention policy.

## 5. Deployment

- [ ] Docker Compose runs backend and optional vector database.
- [ ] Production environment variables are documented.
- [ ] Health endpoint is monitored.
- [ ] Logs are persisted or shipped.
- [ ] Model artifacts are mounted as external volumes.
- [ ] GPU runtime requirements are documented.

## 6. Commercial Pilot Exit Criteria

The project can be called a commercial pilot candidate when all of these are true:

1. strict smoke test passes;
2. real training/evaluation artifacts exist;
3. frontend demo can be shown without manual code edits;
4. release hygiene has no high-risk findings;
5. deployment and rollback steps are documented.