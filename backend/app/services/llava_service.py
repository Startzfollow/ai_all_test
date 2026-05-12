import base64
from pathlib import Path
from typing import Optional

from backend.app.core.config import get_settings


class LlavaService:
    def __init__(self):
        self.settings = get_settings()

    def chat(self, image_path: str, prompt: str, model: Optional[str] = None):
        vlm_cfg = self.settings.vlm
        model_name = model or vlm_cfg.get("model", "llava-local")
        path = Path(image_path)
        if not path.exists():
            return {
                "ok": False,
                "answer": "",
                "model": model_name,
                "message": f"image not found: {image_path}",
            }

        try:
            from openai import OpenAI
            client = OpenAI(api_key=vlm_cfg.get("api_key", "EMPTY"), base_url=vlm_cfg.get("openai_base_url"))
            image_b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
            data_url = f"data:image/{path.suffix.lstrip('.').lower()};base64,{image_b64}"
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }
                ],
            )
            return {"ok": True, "answer": resp.choices[0].message.content or "", "model": model_name, "message": ""}
        except Exception as exc:
            return {
                "ok": True,
                "answer": (
                    "已接收到图像与提示词。当前未连接 VLM 服务，因此返回占位结果。"
                    "你可以用 vLLM/LMDeploy/Ollama 暴露 OpenAI-compatible 接口后，设置 OPENAI_BASE_URL 和 VLM_MODEL。"
                ),
                "model": model_name,
                "message": str(exc),
            }
