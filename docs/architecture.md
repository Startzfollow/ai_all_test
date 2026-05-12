# Architecture

```text
React Frontend
  ├── RAG Panel ───────────────┐
  ├── GUI Agent Panel ─────────┤
  ├── LLaVA/VLM Panel ─────────┤── FastAPI Backend
  └── YOLO Panel ──────────────┘
                                  ├── RAG Service
                                  │   ├── Document Loader
                                  │   ├── Text Splitter
                                  │   ├── Embedding Model
                                  │   └── Qdrant / Local Vector Store
                                  ├── GUI Agent Service
                                  │   ├── Screen Understanding Prompt
                                  │   ├── Task Planner
                                  │   └── Safe Action JSON
                                  ├── LLaVA Service
                                  │   ├── OpenAI-compatible VLM endpoint
                                  │   └── LLaVA-CoT fine-tune configs
                                  └── YOLO Service
                                      ├── Ultralytics Inference
                                      ├── ONNX Export
                                      └── TensorRT Export / Benchmark
```

## 设计原则

1. 所有重模型能力都通过配置注入，本仓库不上传权重。
2. 默认提供本地 fallback，保证项目可启动、可演示。
3. 对 GPU 依赖强的训练/加速部分放在 scripts 中，便于在服务器上单独运行。
4. GUI Agent 默认只 dry-run，避免误操作桌面环境。
