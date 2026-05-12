# YOLO Benchmark Demo Result

## Local Deployment Test

**Model:** YOLOv8n (nano)
**Image:** examples/images/test.jpg

### Command

```bash
python scripts/benchmark_yolo.py --model weights/yolov8n.pt --image examples/images/test.jpg --runs 50 --warmup 5
```

### Output

```json
{
  "runs": 50,
  "mean_ms": 8.73,
  "p50_ms": 8.72,
  "p95_ms": 8.83,
  "fps": 114.57
}
```

## Inference Test

### Command

```python
from backend.app.services.yolo_service import YoloService
svc = YoloService()
result = svc.infer('examples/images/test.jpg', model_path='weights/yolov8n.pt')
```

### Output

```json
{
  "ok": true,
  "detections": [
    {"class_name": "bus", "confidence": 0.87, "xyxy": [22.87, 231.27, 804.94, 756.84]},
    {"class_name": "person", "confidence": 0.87, "xyxy": [48.55, 398.55, 245.35, 902.71]},
    {"class_name": "person", "confidence": 0.85, "xyxy": [669.46, 392.15, 809.72, 877.03]},
    {"class_name": "person", "confidence": 0.83, "xyxy": [221.51, 405.80, 344.98, 857.54]},
    {"class_name": "person", "confidence": 0.26, "xyxy": [0.0, 550.52, 63.02, 873.43]},
    {"class_name": "stop sign", "confidence": 0.26, "xyxy": [0.06, 254.46, 32.56, 324.87]}
  ],
  "latency_ms": 1660.43
}
```

### Features Verified

- YOLO 模型本地加载成功
- 目标检测功能正常
- 支持 .pt 权重格式
- 支持 ONNX/TensorRT 导出脚本