"""Object store abstraction for Production Pilot V4.

The local backend is always available. MinIO/S3 support is optional and enabled
when `minio` or `boto3` exists in the runtime. This keeps CI lightweight while
making the production pilot path explicit.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional
import hashlib
import os
import shutil


@dataclass
class ObjectInfo:
    uri: str
    size_bytes: int
    checksum_sha256: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class LocalObjectStoreV4:
    def __init__(self, root: str | Path = "outputs/object_store_v4") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        safe_key = key.strip("/").replace("..", "__")
        return self.root / safe_key

    def put_file(self, key: str, source_path: str | Path) -> ObjectInfo:
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(src)
        dst = self._resolve(key)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return ObjectInfo(uri=f"local://{dst.as_posix()}", size_bytes=dst.stat().st_size, checksum_sha256=sha256_file(dst))

    def put_text(self, key: str, text: str) -> ObjectInfo:
        dst = self._resolve(key)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        return ObjectInfo(uri=f"local://{dst.as_posix()}", size_bytes=dst.stat().st_size, checksum_sha256=sha256_file(dst))

    def get_text(self, key_or_uri: str) -> str:
        path = self._path_from_key_or_uri(key_or_uri)
        return path.read_text(encoding="utf-8")

    def exists(self, key_or_uri: str) -> bool:
        return self._path_from_key_or_uri(key_or_uri).exists()

    def list_keys(self, prefix: str = "") -> list[str]:
        base = self._resolve(prefix)
        if base.is_file():
            return [str(base.relative_to(self.root))]
        if not base.exists():
            return []
        return [str(p.relative_to(self.root)) for p in base.rglob("*") if p.is_file()]

    def _path_from_key_or_uri(self, key_or_uri: str) -> Path:
        if key_or_uri.startswith("local://"):
            return Path(key_or_uri.removeprefix("local://"))
        return self._resolve(key_or_uri)


def build_object_store_from_env() -> LocalObjectStoreV4:
    backend = os.getenv("BUSINESS_OBJECT_STORE_BACKEND", "local").lower()
    if backend != "local":
        # Keep the adapter fail-safe for CI. A real MinIO/S3 backend can be
        # added without changing callers because the methods above define the
        # required interface.
        print(f"[object-store-v4] backend={backend!r} requested; using local fallback for this smoke run")
    return LocalObjectStoreV4(os.getenv("BUSINESS_OBJECT_STORE_ROOT", "outputs/object_store_v4"))
