"""Minimal production-pilot metrics for field-service AI operations."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class ModuleMetric:
    module: str
    score: float
    release_level: str
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def release_level(score: float) -> str:
    if score >= 0.90:
        return "production_candidate"
    if score >= 0.80:
        return "pilot_candidate"
    if score >= 0.65:
        return "commercial_poc"
    return "technical_demo"


def aggregate_metrics(metrics: List[ModuleMetric]) -> Dict[str, object]:
    if not metrics:
        return {"overall_score": 0.0, "release_level": "technical_demo", "modules": []}
    overall = round(sum(m.score for m in metrics) / len(metrics), 4)
    return {
        "overall_score": overall,
        "release_level": release_level(overall),
        "modules": [m.to_dict() for m in metrics],
    }
