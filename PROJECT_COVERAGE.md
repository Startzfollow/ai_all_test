# 比赛要求覆盖说明

| 官方可能关注点 | 本项目对应模块 | 可展示内容 |
|---|---|---|
| AI Coding / 端到端开发 | FastAPI + React + Docker Compose | 可运行前后端、API 文档、环境配置 |
| GUI Agent | `backend/app/services/gui_agent.py` | 截图输入、任务规划、动作 JSON、dry-run 执行 |
| LLaVA 多模态微调 | `scripts/prepare_llava_cot_data.py`、`configs/llava_lora.yaml`、`scripts/train_llava_lora.sh` | 数据转换、LoRA/QLoRA 配置、训练入口 |
| RAG | `backend/app/services/rag_service.py`、`backend/app/services/vector_store.py` | 文档切分、Embedding、向量检索、知识问答 |
| 多模态算法学习实践 | `scripts/multimodal_retrieval_demo.py`、`backend/app/services/llava_service.py` | 图文检索、图像问答、跨模态流程 |
| YOLO 本地部署加速 | `backend/app/services/yolo_service.py`、`scripts/export_yolo_onnx.py`、`scripts/export_yolo_tensorrt.py`、`scripts/benchmark_yolo.py` | 推理、导出、TensorRT、benchmark |
| 工程能力 | `Makefile`、`environment.yml`、`.env.example`、`docker-compose.yml` | 一键启动、依赖管理、配置化 |

## 简历/报名表推荐描述

> 技术栈：Python、FastAPI、React、Qdrant、RAG、Embedding、LLaVA、LoRA/QLoRA、PyTorch、Transformers、PEFT、YOLO、OpenCV、ONNX、TensorRT、CUDA、Docker、Git。

> 项目职责：完成 AI 多模态全栈应用的整体设计与实现，包括 RAG 知识库问答、GUI Agent 任务规划、LLaVA-CoT 数据处理与微调配置、YOLO 本地推理与部署优化，以及前后端联调和项目工程化交付。
