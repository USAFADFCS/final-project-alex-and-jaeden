from __future__ import annotations
from typing import Dict

def american_to_implied_prob(odds: int) -> float:
    if odds > 0:
        return 100.0 / (odds + 100.0)
    else:
        return (-odds) / ((-odds) + 100.0)

def remove_two_way_vig(p_home_inc_vig: float, p_away_inc_vig: float) -> tuple[float, float]:
    s = p_home_inc_vig + p_away_inc_vig
    if s <= 0:
        raise ValueError("Invalid implied probabilities.")
    return (p_home_inc_vig / s, p_away_inc_vig / s)

def fair_probs_from_moneyline(home_ml: int, away_ml: int) -> Dict[str, float]:
    p_h = american_to_implied_prob(home_ml)
    p_a = american_to_implied_prob(away_ml)
    p_h_fair, p_a_fair = remove_two_way_vig(p_h, p_a)
    return {"home": p_h_fair, "away": p_a_fair}
