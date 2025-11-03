from __future__ import annotations
import json, argparse, pathlib
from fairllm_agent.odds_fetcher import OddsFetcher
from fairllm_agent.probability_calc import fair_probs_from_moneyline
from fairllm_agent.probability_adjuster import edge
from fairllm_agent.report_formatter import build_edge_reports, as_jsonable

def main():
    ap = argparse.ArgumentParser(description="Compute edge vs fair odds using local samples.")
    ap.add_argument("--odds", default="data/samples/odds_demo.json")
    ap.add_argument("--forecast", default="data/samples/forecast_demo.json")
    ap.add_argument("--out", default="edge_report.json")
    args = ap.parse_args()

    odds = OddsFetcher(args.odds).fetch()
    with open(args.forecast) as f:
        forecast = json.load(f)

    fair_p = fair_probs_from_moneyline(odds["moneyline"]["home"], odds["moneyline"]["away"])
    model_p = forecast["p_model"]
    e = edge(model_p, fair_p)
    reports = build_edge_reports(odds["event_id"], odds.get("sportsbook"), fair_p, model_p)
    out = {
        "event_id": odds["event_id"],
        "fair_p": {k: round(v, 4) for k, v in fair_p.items()},
        "model_p": {k: round(v, 4) for k, v in model_p.items()},
        "edge_pct": {k: round(100.0 * v, 2) for k, v in e.items()},
        "reports": as_jsonable(reports),
    }
    pathlib.Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
