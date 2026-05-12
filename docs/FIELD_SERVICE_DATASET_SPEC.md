# Field Service Dataset Specification

This specification defines the dataset used to test the Business Platform V3 workflow.

## Business Scenario

The scenario is **equipment inspection and after-sales support**. A field engineer uploads equipment photos and maintenance documents. The platform should support:

1. RAG knowledge-base construction and question answering.
2. YOLO-style visual inspection dataset validation.
3. LLaVA/VQA-style image question answering samples.
4. GUI Agent task planning samples.
5. Report generation and business acceptance evidence.

## Generated Dataset Layout

```text
data/business_field_service_demo/
├── manifest.json
├── README.md
├── rag_docs/
│   ├── field_unit_a_maintenance_manual.md
│   └── after_sales_troubleshooting_faq.md
├── yolo/
│   ├── data.yaml
│   ├── images/train/*.png
│   ├── images/val/*.png
│   ├── labels/train/*.txt
│   └── labels/val/*.txt
└── eval/
    ├── rag_qa.jsonl
    ├── llava_vqa.jsonl
    └── agent_tasks.jsonl
```

## YOLO Classes

| ID | Class |
|---:|---|
| 0 | gauge |
| 1 | warning_light |
| 2 | serial_plate |
| 3 | corrosion_marker |

## Why Synthetic Data?

Synthetic data provides a safe baseline for acceptance testing:

- no private customer data
- deterministic generation
- stable CI behavior
- small enough for GitHub workflow checks
- aligned with the field-service business story

Real customer datasets can later be registered through `configs/dataset_registry.yaml` and stored outside Git.
