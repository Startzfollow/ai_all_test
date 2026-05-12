# Hardware Environment

This document records the local hardware and software environment used for large-scale multimodal training and inference experiments.

## GPU Environment

Example local environment:

- GPU: 4 × NVIDIA RTX PRO 6000 Blackwell
- GPU Memory: approximately 98 GB per GPU
- CUDA: 13.0
- NVIDIA Driver: 580.126.09
- Training style: multi-GPU distributed training with `torchrun` and DeepSpeed

> Keep this file factual. Update it with the exact output from your own machine before submitting the project.

## Recommended Evidence to Keep

Store generated evidence under:

```text
experiments/<experiment_name>/evidence/<timestamp>/
```

Suggested files:

```text
hardware.txt           # nvidia-smi output
software.json          # Python, PyTorch, CUDA, Transformers, DeepSpeed versions
git.txt                # current git commit and status
config.yaml            # copied experiment config
metrics.json           # final metrics summary
train_tail.log         # last lines of training log
```

## Commands

Collect hardware and software evidence:

```bash
python scripts/collect_training_evidence.py \
  --experiment llava_lora_docvqa \
  --config experiments/llava_lora_docvqa/config.yaml \
  --metrics experiments/llava_lora_docvqa/results/metrics.json
```

The command does not upload checkpoints or private datasets. It only stores reproducibility metadata and small text artifacts.
