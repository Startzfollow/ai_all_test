# Experiment Orchestration

## Goal

Experiments should be repeatable and auditable. The V2 workflow defines each
experiment with a YAML recipe and uses a common launcher to list or execute
commands.

## Experiment Config Directory

```text
configs/experiments/
├── llava_docvqa_lora_v2.yaml
├── rag_bge_reranker_v2.yaml
└── yolo_domain_quality_v2.yaml
```

## Dry-run First

Always list commands before executing:

```bash
python scripts/run_experiment.py \
  --config configs/experiments/llava_docvqa_lora_v2.yaml \
  --list-commands
```

## Execute a Single Step

```bash
python scripts/run_experiment.py \
  --config configs/experiments/llava_docvqa_lora_v2.yaml \
  --step prepare_1k \
  --execute
```

## Execute All Steps

Use this only after verifying every command:

```bash
python scripts/run_experiment.py \
  --config configs/experiments/llava_docvqa_lora_v2.yaml \
  --execute-all
```

## Evidence Discipline

Every real experiment should preserve:

- config file
- command line
- git commit
- hardware info
- software environment
- logs
- metrics
- representative examples
