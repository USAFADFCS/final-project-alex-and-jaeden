from __future__ import annotations
from typing import Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class EdgeReport:
    event_id: str
    side: str
    fair_p: float
    model_p: float
    edge_pct: float
    sportsbook: str | None = None

def build_edge_reports(event_id: str, sportsbook: str | None, fair_p: Dict[str, float], model_p: Dict[str, float]) -> list[EdgeReport]:
    reps = []
    for side in ("home", "away"):
        reps.append(
            EdgeReport(
                event_id=event_id,
                side=side,
                fair_p=round(fair_p[side], 4),
                model_p=round(model_p[side], 4),
                edge_pct=round(100.0 * (model_p[side] - fair_p[side]), 2),
                sportsbook=sportsbook,
            )
        )
    return reps

def as_jsonable(reports: list[EdgeReport]) -> list[Dict[str, Any]]:
    return [asdict(r) for r in reports]
