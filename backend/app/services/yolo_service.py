import time
from pathlib import Path
from typing import Optional

from backend.app.core.config import get_settings


class YoloService:
    def __init__(self):
        self.settings = get_settings()

    def infer(self, image_path: str, model_path: Optional[str] = None, confidence: float = 0.25, image_size: int = 640):
        vision_cfg = self.settings.vision
        model_path = model_path or vision_cfg.get("yolo_model_path", "weights/yolov8n.pt")
        image = Path(image_path)
        model = Path(model_path)
        if not image.exists():
            return {"ok": False, "detections": [], "message": f"image not found: {image_path}", "latency_ms": None}
        if not model.exists():
            return {
                "ok": False,
                "detections": [],
                "message": f"model not found: {model_path}. Put YOLO weights under weights/ or pass model_path.",
                "latency_ms": None,
            }

        try:
            from ultralytics import YOLO
            detector = YOLO(str(model))
            start = time.perf_counter()
            results = detector.predict(source=str(image), imgsz=image_size, conf=confidence, verbose=False)
            latency_ms = (time.perf_counter() - start) * 1000
            detections = []
            names = detector.names
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    detections.append({
                        "class_id": cls_id,
                        "class_name": names.get(cls_id, str(cls_id)) if isinstance(names, dict) else str(cls_id),
                        "confidence": float(box.conf[0]),
                        "xyxy": [float(x) for x in box.xyxy[0].tolist()],
                    })
            return {"ok": True, "detections": detections, "message": "", "latency_ms": latency_ms}
        except Exception as exc:
            return {"ok": False, "detections": [], "message": str(exc), "latency_ms": None}
