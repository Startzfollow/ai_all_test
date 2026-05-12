# Model Weights

Place local model weights here when running inference or export scripts.

Recommended local filenames:

- `yolov8n.pt`
- `yolov8s.pt`
- `yolov8n.onnx`
- `yolov8n.engine`

Large binary model files are intentionally excluded from Git. If a weight file has already been committed, remove it from the Git index while keeping the local file:

```bash
git rm --cached weights/*.pt weights/*.onnx weights/*.engine 2>/dev/null || true
git commit -m "chore: stop tracking local model weights"
```

For public repositories, prefer documenting download or generation steps instead of committing model binaries.
