# Model and Dataset Registry

## Purpose

The model and dataset registry records which local resources are available and
how they are allowed to be used. It prevents the project from relying on vague
claims such as "we have many models" and converts local resources into an
auditable engineering inventory.

## Registry Files

```text
configs/model_registry.yaml
configs/dataset_registry.yaml
```

## Current Local Model Categories

| Category | Example Path | Recommended Use |
|---|---|---|
| LLM / VLM base models | `/mnt/PRO6000_disk/models/Qwen` | LLaVA-style fine-tuning and multimodal inference |
| BAAI models | `/mnt/PRO6000_disk/models/BAAI` | RAG embedding and reranking |
| Tiny BERT baselines | `chinese_tiny_bert`, `english_tiny_bert` | smoke tests and fast baselines |
| Multilingual BERT | `multilingual_bert_model` | multilingual retrieval baseline |
| SmolVLA base | `smolvla_base` | VLA / GUI Agent experiments |

## Current Local Dataset Categories

| Category | Example Path | Recommended Use |
|---|---|---|
| LLaVA-CoT | `/mnt/PRO6000_disk/data/LLaVA-CoT-100k` | VLM instruction tuning |
| LLaVA-R1 | `/mnt/PRO6000_disk/data/LLaVA-R1-100k` | multimodal reasoning |
| DocVQA | `/mnt/PRO6000_disk/data/DocVQA` | document VQA evaluation |
| InfographicVQA | `/mnt/PRO6000_disk/data/InfographicVQA` | chart and infographic reasoning |
| Alpaca-GPT4-ZH | `/mnt/PRO6000_disk/data/alpaca-gpt4-data-zh.json` | Chinese instruction tuning |

## Publication Rules

Do commit:

- registry YAML files
- redacted samples
- metrics
- experiment reports
- small manifests

Do not commit:

- raw private datasets
- model checkpoints
- `.pt`, `.bin`, `.safetensors`, `.onnx`, `.engine`
- unredacted logs containing secrets or private data
