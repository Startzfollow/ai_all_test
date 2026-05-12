# AI Fullstack Multimodal Agent Suite 项目说明

本项目覆盖 GUI Agent、LLaVA 多模态微调、RAG 知识库问答、多模态算法实践、YOLO 本地部署与推理加速。

RAG 模块负责文档解析、文本切分、Embedding 向量化、向量数据库检索和大模型生成。向量库可使用 Qdrant，也可以使用本地 JSON 向量库作为离线 demo。

GUI Agent 模块负责根据用户任务和界面截图生成结构化操作计划，默认使用 dry-run 模式，不直接操作系统。

LLaVA 模块提供 LLaVA-CoT 数据准备、LoRA/QLoRA 微调配置，以及 OpenAI-compatible VLM 推理接口。

YOLO 模块支持目标检测模型本地推理、ONNX 导出、TensorRT 导出和推理 benchmark。
