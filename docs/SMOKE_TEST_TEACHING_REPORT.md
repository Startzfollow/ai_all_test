# Smoke Test Teaching Report

## 1. What a Good Smoke Test Should Prove

A smoke test should not try to prove that the model is excellent. It should prove that the product can breathe:

- the repository structure is complete;
- the backend starts;
- every major feature has a callable path;
- failures are controlled;
- evaluation artifacts can be generated;
- the project is safe to publish.

For this project, the smoke test covers RAG, GUI Agent, LLaVA/VLM, YOLO, training workflow, evaluation workflow, frontend assets, CI, and release hygiene.

## 2. Why We Separate Smoke, Evaluation, and Release Gates

### Smoke

Small, fast, mostly offline. It answers: "Can the system run?"

### Evaluation

Uses metrics. It answers: "Is the result good enough?"

Examples:

- RAG: source hit rate, answer grounding, retrieval recall;
- LLaVA: loss, VQA examples, task accuracy;
- YOLO: latency, FPS, detection sanity.

### Release Gate

Combines smoke, evaluation, security, and deployment.

It answers: "Can this be shown to users or clients?"

## 3. How This Suite Handles Missing Large Models

Commercial systems must degrade gracefully. In a lightweight smoke environment:

- YOLO may not have weights;
- VLM may not have a local OpenAI-compatible endpoint;
- Qdrant may not be running;
- LLaVA full dataset may not be present.

The test passes only if the project handles those situations with stable JSON responses and clear messages.

## 4. Acceptance Scoring

The script assigns each check one of four statuses:

- `PASS`: good for acceptance;
- `WARN`: acceptable for demo but should be fixed;
- `SKIP`: optional heavy check not enabled;
- `FAIL`: must be fixed.

Critical failures block acceptance. Optional checks can be skipped in default mode but should be enabled before commercial release.

## 5. Submission Wording

After default smoke passes:

> The project includes a product-grade smoke acceptance suite covering backend APIs, RAG, GUI Agent, VLM interface, YOLO inference path, LLaVA training assets, evaluation scripts, frontend assets, CI, and release hygiene. The suite generates JSON and Markdown reports under `outputs/smoke`.

After strict smoke and real metrics pass:

> The project has passed strict product acceptance smoke tests and includes real evaluation artifacts for RAG retrieval, LLaVA training, and YOLO latency benchmarking, making it suitable for technical demo and pilot deployment review.