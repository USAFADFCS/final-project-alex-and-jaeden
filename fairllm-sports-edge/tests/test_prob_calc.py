from fairllm_agent.probability_calc import american_to_implied_prob, remove_two_way_vig, fair_probs_from_moneyline

def test_american_to_implied_prob():
    assert round(american_to_implied_prob(-110), 4) == 0.5238
    assert round(american_to_implied_prob(+105), 4) == 0.4878

def test_remove_two_way_vig():
    p_h, p_a = remove_two_way_vig(0.5238, 0.4878)
    assert round(p_h + p_a, 6) == 1.000000

def test_fair_probs_from_moneyline():
    p = fair_probs_from_moneyline(-110, +105)
    assert round(p["home"] + p["away"], 6) == 1.000000
