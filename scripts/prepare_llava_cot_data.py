import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable


def iter_records(input_path: Path) -> Iterable[Dict[str, Any]]:
    files = []
    if input_path.is_dir():
        files.extend(list(input_path.rglob("*.json")))
        files.extend(list(input_path.rglob("*.jsonl")))
        files.extend(list(input_path.rglob("*.csv")))
    else:
        files = [input_path]

    for file in files:
        if file.suffix == ".jsonl":
            for line in file.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.strip():
                    yield json.loads(line)
        elif file.suffix == ".json":
            obj = json.loads(file.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(obj, list):
                for item in obj:
                    yield item
            elif isinstance(obj, dict):
                data = obj.get("data") or obj.get("samples") or obj.get("instances") or [obj]
                if isinstance(data, list):
                    for item in data:
                        yield item
        elif file.suffix == ".csv":
            with file.open("r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield dict(row)


def normalize(item: Dict[str, Any]) -> Dict[str, Any]:
    image = item.get("image") or item.get("image_path") or item.get("image_file") or ""
    question = item.get("question") or item.get("instruction") or item.get("prompt") or "请描述这张图片。"
    answer = item.get("answer") or item.get("response") or item.get("output") or item.get("cot") or ""
    conversations = item.get("conversations")
    if conversations:
        return {"image": image, "conversations": conversations}
    return {
        "image": image,
        "conversations": [
            {"from": "human", "value": f"<image>\n{question}"},
            {"from": "gpt", "value": answer},
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="/mnt/PRO6000_disk/data/LLaVA-CoT-100k")
    parser.add_argument("--output", default="data/processed/llava_cot_train.jsonl")
    parser.add_argument("--max-samples", type=int, default=2000)
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out.open("w", encoding="utf-8") as f:
        for item in iter_records(Path(args.input)):
            f.write(json.dumps(normalize(item), ensure_ascii=False) + "\n")
            count += 1
            if args.max_samples and count >= args.max_samples:
                break
    print({"output": str(out), "samples": count})


if __name__ == "__main__":
    main()
