# LLaVA Scope and Wording Boundaries

## What this repository currently proves

This repository provides:

- LLaVA-style data preparation script
- LoRA/QLoRA training configuration template
- DeepSpeed ZeRO-2 configuration
- VLM/LLaVA API interface for local or OpenAI-compatible model endpoints
- Multimodal demo entrypoints

## What it does not prove by itself

Unless you commit real logs and metrics, the repository does not prove:

- a completed large-scale LLaVA fine-tuning run
- validated improvement on DocVQA / InfographicVQA / LLaVA-CoT benchmark
- production deployment of a fine-tuned VLM

## Safe competition wording

Use this in the application:

> LLaVA 方向主要完成了 LLaVA-style 多模态数据准备、LoRA/QLoRA 微调配置、DeepSpeed ZeRO-2 训练入口和 VLM 推理接口封装，支持后续接入本地多模态模型权重进行训练与评测。

Avoid:

> 已完整完成 LLaVA 大规模微调并达到生产可用效果。

unless you can provide training logs, dataset version, config, checkpoint, and evaluation results.

## Evidence to add later

```text
docs/experiments/llava_train_log_YYYYMMDD.md
outputs/llava_eval_YYYYMMDD.json
configs/llava_lora.yaml
```
