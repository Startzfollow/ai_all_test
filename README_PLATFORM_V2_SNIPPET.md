## Platform V2 Upgrade Snippet

Add this section to README.md after the project status section if desired.

```markdown
## Platform V2: Registry, Experiments, and Quality Gates

This project now includes a registry-driven experiment workflow:

- `configs/model_registry.yaml` records local model families and usage.
- `configs/dataset_registry.yaml` records local datasets and release policy.
- `configs/experiments/` defines repeatable RAG, YOLO, and LLaVA experiment recipes.
- `scripts/scan_local_assets.py` generates a local model/data inventory.
- `scripts/run_experiment.py` lists or executes experiment steps safely.
- `scripts/generate_platform_report.py` consolidates smoke, quality, YOLO, and asset evidence.

Recommended commands:

```bash
python scripts/scan_local_assets.py \
  --models-root /mnt/PRO6000_disk/models \
  --data-root /mnt/PRO6000_disk/data

python scripts/run_experiment.py \
  --config configs/experiments/llava_docvqa_lora_v2.yaml \
  --list-commands

python scripts/evaluate_quality.py --repo-root . --top-k 4
python scripts/generate_platform_report.py --repo-root .
```
```
