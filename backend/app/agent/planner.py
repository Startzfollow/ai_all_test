from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.agent.action_schema import GuiAction
from backend.app.agent.safety import GuiSafetyPolicy
from backend.app.agent.trace import AgentTrace


class GuiAgentPlanner:
    """Safe dry-run GUI Agent planner."""

    def __init__(self):
        self.safety = GuiSafetyPolicy()

    def plan(self, task: str, screenshot_path: Optional[str] = None, dry_run: bool = True) -> Dict[str, Any]:
        trace = AgentTrace()
        trace.add("observe", "received user task", task=task)

        screenshot_exists = bool(screenshot_path and Path(screenshot_path).exists())
        if screenshot_path:
            trace.add(
                "observe",
                "checked screenshot path",
                screenshot_path=screenshot_path,
                exists=screenshot_exists,
            )

        actions = self._heuristic_plan(task)
        trace.add("plan", "created candidate action plan", step_count=len(actions))

        actions = self.safety.validate(actions, dry_run=dry_run)
        trace.add("safety", "applied dry-run and destructive-action policy", dry_run=dry_run)

        notes = "dry-run mode: actions are returned as JSON and not executed."
        if screenshot_path and not screenshot_exists:
            notes += f" screenshot not found: {screenshot_path}."
        trace.add("output", "serialized GUI action plan", notes=notes)

        return {
            "task": task,
            "plan": [action.to_dict() for action in actions],
            "trace": trace.to_list(),
            "dry_run": dry_run,
            "notes": notes,
        }

    def _heuristic_plan(self, task: str) -> List[GuiAction]:
        lower = task.lower()
        if "浏览器" in task or "browser" in lower or "search" in lower or "搜索" in task:
            return [
                GuiAction(
                    action="open_app",
                    target="browser",
                    reason="需要通过浏览器完成搜索或网页操作",
                    confidence=0.86,
                ),
                GuiAction(
                    action="type",
                    target="address_or_search_bar",
                    text=self._extract_query(task),
                    reason="在搜索框或地址栏输入用户目标",
                    confidence=0.82,
                ),
                GuiAction(
                    action="press",
                    target="keyboard",
                    key="enter",
                    reason="提交搜索或打开页面",
                    confidence=0.80,
                ),
            ]
        if "文件" in task or "folder" in lower:
            return [
                GuiAction(
                    action="open_app",
                    target="file_manager",
                    reason="用户目标涉及本地文件或文件夹",
                    confidence=0.78,
                ),
                GuiAction(
                    action="locate",
                    target="requested_file_or_folder",
                    reason="定位用户需要操作的文件对象",
                    confidence=0.72,
                ),
            ]
        return [
            GuiAction(
                action="observe",
                target="screen",
                reason="先理解当前界面状态",
                confidence=0.70,
            ),
            GuiAction(
                action="plan",
                target="ui_elements",
                reason="将用户目标拆成可执行步骤",
                confidence=0.70,
            ),
            GuiAction(
                action="ask_or_execute",
                target="next_best_action",
                reason="低置信度时优先请求确认，避免误操作",
                confidence=0.65,
            ),
        ]

    def _extract_query(self, task: str) -> str:
        for token in ["搜索", "search"]:
            if token in task:
                return task.split(token, 1)[-1].strip(" ：:，,。") or task
        return task
