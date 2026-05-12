from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional


def default_object_store_root() -> Path:
    return Path(os.getenv("BUSINESS_OBJECT_STORE_ROOT", "outputs/object_store"))


class ObjectStore:
    """Minimal object storage abstraction.

    Local mode stores files under outputs/object_store and returns local:// URIs.
    For commercial deployment, run MinIO/S3 and replace this adapter without changing task APIs.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or default_object_store_root()
        self.root.mkdir(parents=True, exist_ok=True)

    def put_bytes(self, bucket: str, key: str, content: bytes) -> str:
        safe_key = key.strip("/").replace("..", "_")
        path = self.root / bucket / safe_key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return f"local://{bucket}/{safe_key}"

    def put_text(self, bucket: str, key: str, text: str) -> str:
        return self.put_bytes(bucket, key, text.encode("utf-8"))

    def put_file(self, bucket: str, source_path: str, key: Optional[str] = None) -> str:
        path = Path(source_path)
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()[:12]
        final_key = key or f"{digest}_{path.name}"
        return self.put_bytes(bucket, final_key, data)

    def resolve(self, uri: str) -> Path:
        if not uri.startswith("local://"):
            raise ValueError(f"Only local:// URIs are supported by the lightweight adapter: {uri}")
        _, rest = uri.split("local://", 1)
        return self.root / rest
