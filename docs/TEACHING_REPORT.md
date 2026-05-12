# AI Fullstack Multimodal Agent Suite 深度改进教学报告

## 1. 改进目标

本轮改进围绕 6 个目标展开：

1. 仓库 flatten：让 GitHub 根目录直接呈现项目主体。
2. 补截图：形成可验证的演示证据。
3. RAG 分层重构：把 RAG 从单文件服务改为可测试、可替换的工程 pipeline。
4. GUI Agent trace：让 GUI Agent 输出动作计划的同时展示 observe / plan / safety / output 过程。
5. YOLO benchmark 真实数据：提供真实测量脚本，不编造加速数据。
6. LLaVA 表述边界：区分“已提供微调入口”和“已完成大规模训练”。

## 2. 仓库 flatten 教学

如果仓库根目录只看到一个 `ai-fullstack-multimodal-agent-suite/` 子目录，评审会觉得这是解压包或临时上传。正式项目应把 `backend/`、`frontend/`、`README.md` 等放在根目录。

执行：

```bash
bash ai-fullstack-multimodal-agent-suite/scripts/flatten_repository.sh ai-fullstack-multimodal-agent-suite
git add .
git commit -m "chore: flatten repository structure"
```

## 3. 截图证据教学

文档中的功能描述需要截图支撑。建议至少提交：

- `docs/assets/api_docs.png`
- `docs/assets/frontend_dashboard.png`
- `docs/assets/gui_agent_trace.png`

自动截图：

```bash
pip install playwright
python -m playwright install chromium
python scripts/capture_demo_screenshots.py
```

## 4. RAG 分层教学

RAG 的核心不是“用了向量库”，而是完整链路：

```text
document -> chunk -> embedding -> vector store -> retrieve -> rerank -> generate
```

本补丁新增 `backend/app/rag/`，并保留旧 `RagService` 作为兼容 wrapper。这样 API 不变，但内部结构更专业。

运行评估：

```bash
python scripts/eval_rag.py --documents-dir examples/docs --top-k 4
```

## 5. GUI Agent trace 教学

GUI Agent 如果只返回动作 JSON，会显得像规则脚本。加入 trace 后，可以展示智能体式流程：

```text
observe: 收到任务和截图
plan: 生成候选动作
safety: 加 dry-run 和风险标记
output: 序列化返回
```

这对比赛展示很有价值，因为评审可以看到可解释过程和安全边界。

## 6. YOLO benchmark 教学

YOLO 加速不能写虚假倍数。正确做法是：

1. 跑 `.pt` baseline。
2. 导出 `.onnx` 后跑 ONNX Runtime。
3. 导出 `.engine` 后跑 TensorRT。
4. 把每次输出 JSON 放进 `outputs/`，再摘要写入 `docs/demo_yolo_benchmark.md`。

命令：

```bash
python scripts/benchmark_yolo.py --model weights/yolov8n.pt --image examples/images/demo.png --runs 100
```

## 7. LLaVA 边界教学

当前仓库适合说“提供 LLaVA-style 数据准备、LoRA/QLoRA 微调入口和推理接口”，不要说“已完成大规模 LLaVA 微调”。

推荐表述：

> LLaVA 方向主要完成了 LLaVA-style 多模态数据准备、LoRA/QLoRA 微调配置、DeepSpeed ZeRO-2 训练入口和 VLM 推理接口封装，支持后续接入本地多模态模型权重进行训练与评测。

## 8. 推荐提交顺序

```bash
git add scripts/flatten_repository.sh docs/REPOSITORY_FLATTEN.md
git commit -m "chore: add repository flatten guide"

git add backend/app/rag backend/app/services/rag_service.py backend/tests/test_rag_layered.py scripts/eval_rag.py
git commit -m "feat: refactor RAG into layered pipeline"

git add backend/app/agent backend/app/services/gui_agent.py backend/app/schemas.py backend/tests/test_agent_trace.py frontend/src
git commit -m "feat: add GUI agent trace and dashboard tabs"

git add scripts/benchmark_yolo.py docs/YOLO_BENCHMARK.md weights/README.md .gitignore
git commit -m "feat: add real YOLO benchmark workflow"

git add docs/LLAVA_SCOPE_AND_BOUNDARIES.md docs/SCREENSHOT_GUIDE.md scripts/capture_demo_screenshots.py
git commit -m "docs: add demo evidence and model scope boundaries"

git add .github/workflows/ci.yml pyproject.toml .pre-commit-config.yaml Makefile
git commit -m "ci: add tests and quality tooling"
```

## 9. 最后验收清单

- [ ] GitHub 根目录已 flatten。
- [ ] `pytest -q` 通过。
- [ ] `python scripts/eval_rag.py` 能生成 JSON。
- [ ] `python scripts/benchmark_yolo.py` 在有权重时能生成真实 benchmark JSON。
- [ ] README 有项目状态、截图、运行命令和表述边界。
- [ ] 不再追踪大模型权重、zip、output、`__pycache__`。
