# Field Service Multimodal AI Ops Platform

面向设备巡检与售后场景的多模态 AI 全栈平台原型。

## 项目概述

本项目是一个 AI 全栈多模态应用实践仓库，围绕真实业务场景构建了 RAG 知识库问答、GUI Agent 操作规划、LLaVA 多模态微调流程、YOLO 本地部署与推理加速等模块。后端基于 FastAPI 提供统一 API，前端基于 React 完成交互演示，向量检索使用 Qdrant/本地向量库，模型侧支持本地大模型、Embedding 模型、视觉语言模型和目标检测模型接入。项目重点关注从算法验证到工程落地的完整流程，包括数据处理、模型推理、微调配置、服务封装、前后端联调和线上交付。

## 核心功能

- **RAG 知识库问答**：文档解析、文本切分、Embedding、Qdrant/本地向量库、检索增强生成
- **GUI Agent**：截图理解、任务规划、动作 JSON 输出、工具调用与安全 dry-run 执行
- **LLaVA 多模态微调**：LLaVA-CoT 数据准备、LoRA/QLoRA 配置、训练脚本模板、推理服务接口
- **YOLO 本地部署**：目标检测推理、ONNX/TensorRT 导出、benchmark 脚本
- **全栈应用交付**：FastAPI 后端 + React 前端 + Docker Compose

## 快速启动

```bash
# 安装依赖
pip install fastapi uvicorn pydantic pydantic-settings pyyaml numpy pytest httpx

# 启动后端服务
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# 访问 API 文档
# http://127.0.0.1:8000/docs

# 运行产品验收测试
python scripts/product_smoke_acceptance.py
```

## 项目结构

```
backend/              # FastAPI 后端
frontend/             # React 前端
configs/              # 配置文件
data/                 # 数据集
docs/                 # 文档
experiments/          # 实验配置
outputs/              # 输出结果
scripts/              # 工具脚本
weights/              # 模型权重
```
