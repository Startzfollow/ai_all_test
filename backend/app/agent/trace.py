from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class TraceEvent:
    stage: str
    message: str
    timestamp_ms: int
    data: Dict[str, Any] = field(default_factory=dict)


class AgentTrace:
    """Trace recorder for GUI-agent planning.

    Trace data is useful for demos: it shows observe -> plan -> safety -> output
    instead of returning an opaque JSON list.
    """

    def __init__(self):
        self.started = time.time()
        self.events: List[TraceEvent] = []

    def add(self, stage: str, message: str, **data: Any) -> None:
        elapsed_ms = int((time.time() - self.started) * 1000)
        self.events.append(TraceEvent(stage=stage, message=message, timestamp_ms=elapsed_ms, data=data))

    def to_list(self) -> List[Dict[str, Any]]:
        return [asdict(event) for event in self.events]
