import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="weights/yolov8n.pt")
    parser.add_argument("--output", default="weights/yolov8n.engine")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--half", action="store_true")
    args = parser.parse_args()

    from ultralytics import YOLO
    model = YOLO(args.model)
    exported = model.export(format="engine", imgsz=args.imgsz, half=args.half)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    print({"exported": str(exported), "target": str(out)})


if __name__ == "__main__":
    main()
