# Experiments

This directory contains reproducible experiment definitions and small evidence artifacts.

## Directory Convention

Each experiment should follow this structure:

```text
experiments/<experiment_name>/
├── README.md
├── config.yaml
├── train.sh
├── eval.sh
├── logs/
├── results/
│   ├── metrics.json
│   └── examples.jsonl
└── evidence/
```

## What Should Be Committed

Commit:

- training configs
- launch scripts
- small logs or log tails
- metrics JSON
- selected inference examples
- evidence metadata
- notes and README files

Do not commit:

- raw private datasets
- full checkpoints
- `.pt`, `.bin`, `.safetensors`, `.engine`, `.onnx` model artifacts
- huge logs
- credentials or API keys

## Suggested Workflow

```bash
python scripts/prepare_llava_training_subset.py --help
python scripts/validate_llava_dataset.py --help
bash experiments/llava_lora_docvqa/train.sh
bash experiments/llava_lora_docvqa/eval.sh
python scripts/collect_training_evidence.py --help
python scripts/render_training_report.py --help
```
