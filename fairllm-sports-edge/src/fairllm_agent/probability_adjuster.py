from __future__ import annotations
from typing import Dict

def blend_model_with_fair(fair_p: Dict[str, float], model_p: Dict[str, float], alpha: float = 0.5) -> Dict[str, float]:
    alpha = max(0.0, min(1.0, alpha))
    return {
        "home": (1 - alpha) * fair_p["home"] + alpha * model_p["home"],
        "away": (1 - alpha) * fair_p["away"] + alpha * model_p["away"],
    }

def edge(model_p: Dict[str, float], fair_p: Dict[str, float]) -> Dict[str, float]:
    """Calculate betting edge as percentage"""
    return {"home": (model_p["home"] - fair_p["home"]) * 100, "away": (model_p["away"] - fair_p["away"]) * 100}