# Database, Object Storage, and Monitoring

## Database

本地 smoke 默认：

```bash
BUSINESS_DB_URL=sqlite:///outputs/business_ops.db
```

商业 PoC 推荐：

```bash
BUSINESS_DB_URL=postgresql://postgres:postgres@localhost:5432/ai_ops
```

表：

- `projects`
- `assets`
- `tasks`
- `model_assets`
- `dataset_assets`
- `evaluations`
- `events`

## Object Storage

默认本地对象存储：

```bash
BUSINESS_OBJECT_STORE_ROOT=outputs/object_store
```

URI 格式：

```text
local://business-assets/<project>/<file>
```

商业 PoC 可替换为 MinIO/S3。

## Monitoring

最小监控包括：

- `/api/business/monitoring/health`
- `/api/business/monitoring/gpu`
- 任务状态表
- 失败事件表
- worker stdout 日志

这不是完整 APM，但足够支撑 PoC 验收。
