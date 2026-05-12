from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class GuiAction:
    """A single safe GUI action emitted by the planner."""

    action: str
    target: str
    reason: str
    text: Optional[str] = None
    key: Optional[str] = None
    confidence: float = 0.75
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v not in (None, {}, [])}
