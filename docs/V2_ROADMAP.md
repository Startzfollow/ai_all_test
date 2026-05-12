# V2 Roadmap

## Phase 1: Registry and Inventory

- [x] Add model registry
- [x] Add dataset registry
- [x] Add local asset scanner
- [ ] Attach generated asset report to README or docs

## Phase 2: Experiment Recipes

- [x] Add LLaVA LoRA experiment recipe
- [x] Add RAG embedding/reranker recipe
- [x] Add YOLO domain quality recipe
- [ ] Add GUI Agent task benchmark recipe

## Phase 3: Real Quality Improvement

- [ ] Replace RAG smoke embedding with stronger BAAI embedding
- [ ] Add reranker evaluation
- [ ] Build 50-100 question RAG evaluation set
- [ ] Compare YOLOv8n and YOLOv8s on a domain validation set
- [ ] Run LLaVA 1k smoke training and record loss curve
- [ ] Run 10k medium multimodal training experiment

## Phase 4: Productization

- [ ] Add authentication or API key layer
- [ ] Add request logging and audit records
- [ ] Add model/version selection in frontend
- [ ] Add Docker Compose deployment profile for local GPU server
- [ ] Add screenshot evidence for backend API, frontend, RAG, YOLO, and quality reports

## Phase 5: Commercial Pilot Candidate

- [ ] Product Smoke 100% pass
- [ ] Quality score >= 0.80
- [ ] RAG Recall@3 >= 0.80 on evaluation set
- [ ] YOLO mAP50 >= 0.70 on domain dataset
- [ ] GUI Agent unsafe action rate = 0
- [ ] LLaVA evaluation evidence available
