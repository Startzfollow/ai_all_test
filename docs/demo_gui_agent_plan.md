# GUI Agent Demo Result

## Dry-run Plan Test

**Task:** "打开浏览器搜索 LLaVA 多模态微调"

### Command

```bash
python scripts/run_mini_demo.py
```

### Output

```json
{
  "task": "打开浏览器搜索 LLaVA 多模态微调",
  "plan": [
    {
      "action": "open_app",
      "target": "browser",
      "reason": "需要通过浏览器完成搜索或网页操作"
    },
    {
      "action": "type",
      "text": "LLaVA 多模态微调",
      "target": "address_or_search_bar"
    },
    {
      "action": "press",
      "key": "enter"
    }
  ],
  "dry_run": true,
  "notes": "dry-run mode: actions are returned as JSON and not executed."
}
```

### Features Verified

- GUI Agent 接收任务描述
- 生成结构化操作计划 (JSON)
- 支持 dry-run 模式（不实际执行动作）
- 包含 action, target, reason 字段