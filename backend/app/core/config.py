import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel


def deep_update(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = value
    return base


class Settings(BaseModel):
    app_name: str = "AI Fullstack Multimodal Agent Suite"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    raw: Dict[str, Any]

    @property
    def rag(self) -> Dict[str, Any]:
        return self.raw.get("rag", {})

    @property
    def paths(self) -> Dict[str, Any]:
        return self.raw.get("paths", {})

    @property
    def llm(self) -> Dict[str, Any]:
        return self.raw.get("llm", {})

    @property
    def vlm(self) -> Dict[str, Any]:
        return self.raw.get("vlm", {})

    @property
    def vision(self) -> Dict[str, Any]:
        return self.raw.get("vision", {})

    @property
    def gui_agent(self) -> Dict[str, Any]:
        return self.raw.get("gui_agent", {})


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    config_path = Path(os.getenv("CONFIG_PATH", "configs/default.yaml"))
    raw: Dict[str, Any] = {}
    if config_path.exists():
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    # Environment overrides
    raw.setdefault("rag", {})
    raw["rag"]["vector_backend"] = os.getenv("VECTOR_BACKEND", raw["rag"].get("vector_backend", "local"))
    raw["rag"]["qdrant_url"] = os.getenv("QDRANT_URL", raw["rag"].get("qdrant_url", "http://127.0.0.1:6333"))
    raw["rag"]["qdrant_collection"] = os.getenv("QDRANT_COLLECTION", raw["rag"].get("qdrant_collection", "ai_fullstack_docs"))
    raw["rag"]["embedding_model_path"] = os.getenv("EMBEDDING_MODEL_PATH", raw["rag"].get("embedding_model_path", "/mnt/PRO6000_disk/models/BAAI"))

    raw.setdefault("llm", {})
    raw["llm"]["openai_base_url"] = os.getenv("OPENAI_BASE_URL", raw["llm"].get("openai_base_url", "http://127.0.0.1:8001/v1"))
    raw["llm"]["api_key"] = os.getenv("OPENAI_API_KEY", raw["llm"].get("api_key", "EMPTY"))
    raw["llm"]["model"] = os.getenv("LLM_MODEL", raw["llm"].get("model", "qwen-local"))

    raw.setdefault("vlm", {})
    raw["vlm"]["openai_base_url"] = os.getenv("OPENAI_BASE_URL", raw["vlm"].get("openai_base_url", "http://127.0.0.1:8001/v1"))
    raw["vlm"]["api_key"] = os.getenv("OPENAI_API_KEY", raw["vlm"].get("api_key", "EMPTY"))
    raw["vlm"]["model"] = os.getenv("VLM_MODEL", raw["vlm"].get("model", "llava-local"))

    raw.setdefault("paths", {})
    raw["paths"]["models_root"] = os.getenv("MODELS_ROOT", raw["paths"].get("models_root", "/mnt/PRO6000_disk/models"))
    raw["paths"]["data_root"] = os.getenv("DATA_ROOT", raw["paths"].get("data_root", "/mnt/PRO6000_disk/data"))

    app = raw.get("app", {})
    return Settings(
        app_name=app.get("name", "AI Fullstack Multimodal Agent Suite"),
        app_host=os.getenv("APP_HOST", app.get("host", "0.0.0.0")),
        app_port=int(os.getenv("APP_PORT", app.get("port", 8000))),
        raw=raw,
    )
