# Model and Data Management

This repository is designed to work with local model and dataset directories without committing large files to Git.

## Local Model Layout

The default config supports a local model root such as:

```text
/mnt/PRO6000_disk/models/
├── BAAI
├── Qwen
├── chinese_tiny_bert
├── english_tiny_bert
├── multilingual_bert_model
└── smolvla_base
```

These paths are configured through `configs/default.yaml` and should be treated as runtime configuration rather than repository content.

## Local Dataset Layout

The project can reference local datasets such as:

```text
/mnt/PRO6000_disk/data/
├── LLaVA-CoT-100k
├── LLaVA-R1-100k
├── DocVQA
├── InfographicVQA
├── alpaca-gpt4-data-zh.json
└── train.csv
```

Large datasets should not be committed. Keep only tiny samples under `examples/` or `data/processed/*sample*.jsonl` for documentation and tests.

## Recommended Git Policy

Tracked:

- configs
- source code
- scripts
- docs
- tiny sample files
- reproducible experiment logs

Ignored:

- model weights: `*.pt`, `*.onnx`, `*.engine`, `*.safetensors`
- generated vector stores
- raw datasets
- benchmark outputs
- Python cache files

## LLaVA-style Fine-tuning Scope

Current repository scope:

- data conversion script
- LoRA / QLoRA config template
- DeepSpeed ZeRO-2 config
- training entrypoint

Do not claim a full large-scale fine-tuning run unless the repository includes real logs, training config, data version, runtime, GPU information and produced adapter artifacts.
