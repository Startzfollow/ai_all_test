# Business Task System

## 任务类型

| Task Type | 用户价值 | 执行方式 |
|---|---|---|
| `rag_build` | 将维修手册和业务文档转为可问答知识库 | 调用 RAG 评估/建库脚本 |
| `yolo_benchmark` | 验证现场图片检测速度和可用性 | 调用 YOLO benchmark 脚本 |
| `llava_train` | 规划或启动多模态 LoRA 微调 | 默认 planned，避免误触发长训练 |
| `report_generate` | 汇总任务和评估结果 | 写入 JSON 报告 |

## 最简异步架构

1. API 创建任务，状态为 `pending`；
2. Worker 扫描 pending 任务；
3. 执行任务并写入 `succeeded` 或 `failed`；
4. 结果写入 `tasks.result_json`；
5. 指标写入 `evaluations`；
6. 失败写入 `events`。

运行：

```bash
python scripts/run_business_worker.py
```

持续运行：

```bash
python scripts/run_business_worker.py --loop --interval 5
```
