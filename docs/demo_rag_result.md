# RAG Demo Result

## Query Test

**Query:** "项目覆盖哪些技术栈？"

### Command

```bash
python scripts/run_mini_demo.py
```

### Output

```json
{
  "answer_preview": "根据已检索到的资料，和问题最相关的内容如下：\n\n[1] # 技术栈\n后端使用 Python、FastAPI、Pydantic、Uvicorn。\n前端使用 React、Vite、CSS。\nRAG 使用 Embedding、Qdrant、文本切分、相似度检索和提示词增强生成。\n多模态方向涉及 LLaVA、LLaVA-CoT、图像理解、视觉问答、图文对齐和 LoRA 微调。\n视觉检测方向使用 YOLO、OpenCV、ONNX、TensorRT、CUDA。\n工程化部分包含 Docker Compose、Makefile、环境变量、配置文件和 GitHub 推送脚本。\n\n[2] # AI Fullstack Multimodal Agent Suite 项目说明\n本项目覆盖 GUI Agent、LLaVA 多模态微调、RAG 知识库问答、多模态算法实践、YOLO 本地部署与推理加速。\nRAG 模块负责文档解析、文本切分、Embedding 向量化、向量数据库检索和大模型生成。向量库可使用 Qdrant，也可以使用本地 JSON 向量库作为离线 demo。",
  "sources": [
    {
      "score": 0.0625,
      "source": "examples/docs/tech_stack.md",
      "text_preview": "# 技术栈 后端使用 Python、FastAPI、Pydantic、Uvicorn。 前端使用 React、Vite、CSS。 RAG 使用 Embedding、Qdrant、文本切分、相似度检索和提示词增强生成。 多模态方向涉及 LLa"
    },
    {
      "score": 0.0275,
      "source": "examples/docs/project_overview.md",
      "text_preview": "# AI Fullstack Multimodal Agent Suite 项目说明 本项目覆盖 GUI Agent、LLaVA 多模态微调、RAG 知识库问答、多模态算法实践、YOLO 本地部署与推理加速。 RAG 模块负责文档解析、文本切"
    }
  ]
}
```

### Modules Verified

- RAG 文档导入成功 (2 篇文档)
- 向量检索正常
- 上下文拼接正常