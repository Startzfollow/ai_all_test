# Mini Demo

这个最小演示不依赖外部模型下载，也不要求 Qdrant、LLaVA 或 YOLO 权重。它用于先证明项目的端到端接口可以跑通。

```bash
python scripts/run_mini_demo.py
```

会依次验证：

1. FastAPI 服务入口与健康检查
2. RAG 文档导入
3. RAG 本地向量检索问答
4. GUI Agent dry-run 任务规划
5. LLaVA-compatible 多模态接口占位返回
6. YOLO 推理接口的权重缺失提示

真实模型接入方式：

- RAG：将 `configs/default.yaml` 中的向量库切到 Qdrant，或保持本地 JSON demo。
- LLaVA/VLM：用 vLLM、LMDeploy 或 Ollama 暴露 OpenAI-compatible 接口，配置 `OPENAI_BASE_URL` 和 `VLM_MODEL`。
- YOLO：把 `.pt`、`.onnx` 或 `.engine` 权重放到 `weights/`，再调用 `/api/vision/yolo/infer`。
