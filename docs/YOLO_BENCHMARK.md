# YOLO Benchmark Teaching Note

## Important boundary

Do not write fake acceleration numbers. Run the benchmark script on the target machine and paste the generated JSON summary into `docs/demo_yolo_benchmark.md`.

## Benchmark command

```bash
python scripts/benchmark_yolo.py \
  --model weights/yolov8n.pt \
  --image examples/images/demo.png \
  --imgsz 640 \
  --device 0 \
  --warmup 10 \
  --runs 100
```

The script writes:

```text
outputs/yolo_benchmark_YYYYMMDD_HHMMSS.json
```

## What to report

| Field | Meaning |
|---|---|
| `avg_latency_ms` | average end-to-end inference latency |
| `p50_latency_ms` | median latency |
| `p90_latency_ms` | 90th percentile latency |
| `p95_latency_ms` | 95th percentile latency |
| `fps` | estimated throughput for single-image inference |
| `hardware` | GPU, driver, CUDA and PyTorch environment |

## Suggested benchmark matrix

| Model | Backend | Precision | Image Size | Runs | Avg Latency | FPS |
|---|---|---|---:|---:|---:|---:|
| YOLOv8n | PyTorch `.pt` | FP32/AMP runtime | 640 | 100 | measured | measured |
| YOLOv8n | ONNX `.onnx` | FP32 | 640 | 100 | measured | measured |
| YOLOv8n | TensorRT `.engine` | FP16 | 640 | 100 | measured | measured |

## README wording

Use:

> YOLO 模块提供本地推理、ONNX/TensorRT 导出脚本和 benchmark 工具，支持在本机 GPU 上生成真实推理延迟数据。

Avoid:

> YOLO 已经实现 TensorRT 加速 X 倍。

unless the measured report is committed.
