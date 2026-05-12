# Business Platform V3: 设备巡检与售后知识助手

## 业务定位

本改版把通用 AI Demo 收敛成一个明确业务：**面向现场工程师的多模态设备巡检与售后知识助手**。

用户需求：上传设备图片、PDF/文本维修手册和检测图片后，系统帮助完成：

1. 维修手册 RAG 建库和问答；
2. 现场图片 YOLO 检测与延迟评估；
3. LLaVA-style 多模态 LoRA 训练任务规划；
4. 结果报告生成；
5. GPU、任务状态、失败信息的最小监控。

## 为什么这仍是全栈

| 层级 | V3 能力 |
|---|---|
| UI | 默认单工作台 UI，不做用户系统 |
| API | `/api/business/*` 业务 API |
| 异步任务 | DB-backed task queue，支持 worker 或同步验收 |
| 数据库 | SQLite 本地 smoke，PostgreSQL 商业 PoC |
| 对象存储 | local:// 适配器，后续替换 MinIO/S3 |
| AI 能力 | RAG、YOLO benchmark、LLaVA training plan、report generation |
| 监控 | GPU snapshot、task status、failure events |
| 验收 | `scripts/business_platform_smoke.py` |

## 商业边界

这个版本是商业 PoC 候选，而不是完整 SaaS。它没有多租户、计费、复杂 RBAC 和 SLA，但已经具备面向单客户/单业务场景试点的工程闭环。
