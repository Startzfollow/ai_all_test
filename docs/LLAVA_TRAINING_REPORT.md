# LLaVA-style Multimodal Training Report

## 1. Objective

This experiment fine-tunes a LLaVA-style multimodal model on visual question answering and reasoning data.

The goal is to improve:

- image understanding
- document question answering
- chart reasoning
- multimodal instruction following

## 2. Training Scope

The repository provides the following concrete training assets:

- LLaVA-style data preparation and validation scripts
- LoRA / QLoRA training experiment directory
- DeepSpeed distributed training configuration
- metrics and example-output templates
- evidence collection script for hardware, software, config, git commit, and logs
- reporting script for generating reproducible experiment documentation

Large model checkpoints and raw datasets are intentionally excluded from Git.

## 3. Hardware Environment

Example local environment:

- GPU: 4 × NVIDIA RTX PRO 6000 Blackwell
- GPU memory: approximately 98 GB per GPU
- CUDA: 13.0
- Driver: 580.126.09
- Training framework: PyTorch + Transformers + DeepSpeed

Before final submission, update this section with evidence collected by:

```bash
python scripts/collect_training_evidence.py \
  --experiment llava_lora_docvqa \
  --config experiments/llava_lora_docvqa/config.yaml \
  --metrics experiments/llava_lora_docvqa/results/metrics.json \
  --log experiments/llava_lora_docvqa/logs/train.log
```

## 4. Dataset Sources

Local datasets prepared for training may include:

- LLaVA-CoT-100k
- LLaVA-R1-100k
- DocVQA
- InfographicVQA
- Alpaca-GPT4-ZH

The training data is converted into a LLaVA-style conversation format:

```json
{
  "image": "relative/or/absolute/image/path.jpg",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\nPlease answer the question based on the image."
    },
    {
      "from": "gpt",
      "value": "The answer is ..."
    }
  ]
}
```

## 5. Training Strategy

Recommended staged process:

1. 1k-sample smoke test
2. 10k to 30k medium-scale run
3. full dataset run
4. evaluation with VQA-style prompts
5. inference integration through FastAPI

## 6. Training Configuration

Default experiment path:

```text
experiments/llava_lora_docvqa/config.yaml
```

Default strategy:

- Method: LoRA / QLoRA
- Precision: bf16
- Distributed training: DeepSpeed ZeRO-2
- LoRA rank: 64
- LoRA alpha: 128
- Learning rate: 2e-5
- Gradient checkpointing: enabled
- Gradient accumulation: enabled

## 7. Evidence Files

After a real run, keep:

```text
experiments/llava_lora_docvqa/results/metrics.json
experiments/llava_lora_docvqa/results/examples.jsonl
experiments/llava_lora_docvqa/evidence/hardware.txt
experiments/llava_lora_docvqa/evidence/software.json
experiments/llava_lora_docvqa/evidence/git.txt
```

## 8. Safe Project Wording

Recommended wording:

> This project supports and demonstrates large-scale LLaVA-style multimodal training through data preparation, LoRA/QLoRA configuration, multi-GPU DeepSpeed training scripts, training evidence collection, evaluation output templates, and fullstack inference integration.

Use stronger claims only after the corresponding evidence is committed:

- completed training logs
- metrics JSON
- inference examples
- evaluation report
- hardware/software evidence