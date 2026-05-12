# Business Dataset Acceptance Report

- Passed: `True`
- Score: `1.0`
- Release level: `pilot_candidate`
- Dataset root: `data/business_field_service_demo`

## Checks

### manifest
- **Passed**: true
- **Name**: field_service_demo_dataset

### rag_docs
- **Passed**: true
- **Count**: 2 documents

### yolo_labels
- **Passed**: true
- **Image count**: 16
- **Label count**: 16
- **Missing labels**: []
- **Invalid labels**: []

### eval_files
| File | Passed | Count |
|------|--------|-------|
| rag_qa.jsonl | true | 3 |
| llava_vqa.jsonl | true | 12 |
| agent_tasks.jsonl | true | 2 |

### business_smoke
- **Passed**: true
- **Return code**: 0
- **Business Platform V3**: All checks passed

### quality_eval
- **Passed**: true
- **Overall score**: 0.625
- **Release level**: technical_demo

## GPU Monitoring
- **Available**: true
- **GPU 0**: NVIDIA RTX PRO 6000 Blackwell, 4453 MB used, 31% util, 64°C
- **GPU 1**: NVIDIA RTX PRO 6000 Blackwell, 18 MB used, 0% util, 33°C
- **GPU 2**: NVIDIA RTX PRO 6000 Blackwell, 18 MB used, 0% util, 34°C
- **GPU 3**: NVIDIA RTX PRO 6000 Blackwell, 18 MB used, 0% util, 31°C

---
Generated: 2026-05-12
