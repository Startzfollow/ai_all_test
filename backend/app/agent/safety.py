from __future__ import annotations

from typing import Iterable, List

from backend.app.agent.action_schema import GuiAction

DESTRUCTIVE_ACTIONS = {"delete", "submit_payment", "send_email", "format_disk", "install_package"}


class GuiSafetyPolicy:
    """Safety gate for GUI actions.

    The default project mode is dry-run. This policy marks destructive operations
    for review even if a future executor is added.
    """

    def validate(self, actions: Iterable[GuiAction], dry_run: bool = True) -> List[GuiAction]:
        safe_actions: List[GuiAction] = []
        for action in actions:
            if action.action in DESTRUCTIVE_ACTIONS:
                action.metadata["requires_human_review"] = True
                action.metadata["safety_reason"] = "destructive action is not executed automatically"
            if dry_run:
                action.metadata["dry_run"] = True
            safe_actions.append(action)
        return safe_actions
