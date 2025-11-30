"""
Agentic Workflow for Sports Edge Analysis
Uses FairLLM framework to coordinate multiple specialized agents
"""
from __future__ import annotations
from typing import Dict, Any, List
import json

# Mock Fair classes if FairLLM not available
try:
    from fair import Agent, Flow
except ImportError:
    class Agent:
        """Mock Agent class for when FairLLM is not installed"""
        def __init__(self, name: str = "Agent"):
            self.name = name
    
    class Flow:
        """Mock Flow class for when FairLLM is not installed"""
        def __init__(self, name: str = "Flow"):
            self.name = name

from fairllm_agent.probability_calc import fair_probs_from_moneyline
from fairllm_agent.probability_adjuster import edge
from fairllm_agent.report_formatter import build_edge_reports, as_jsonable


class OddsAnalyzerAgent(Agent):
    """Agent responsible for analyzing sportsbook odds and extracting fair probabilities"""
    
    def __init__(self, name: str = "OddsAnalyzer"):
        super().__init__(name=name)
        self.expertise = "Converting American odds to fair probabilities by removing vig"
    
    def analyze_odds(self, odds_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze odds data and compute fair probabilities
        
        Args:
            odds_data: Dictionary containing event and moneyline odds
            
        Returns:
            Dictionary with fair probabilities and metadata
        """
        moneyline = odds_data.get("moneyline", {})
        home_ml = moneyline.get("home")
        away_ml = moneyline.get("away")
        
        if home_ml is None or away_ml is None:
            raise ValueError("Invalid moneyline data")
        
        # Calculate fair probabilities by removing vig
        fair_p = fair_probs_from_moneyline(home_ml, away_ml)
        
        return {
            "event_id": odds_data.get("event_id"),
            "sport": odds_data.get("sport"),
            "league": odds_data.get("league"),
            "home_team": odds_data.get("home_team"),
            "away_team": odds_data.get("away_team"),
            "sportsbook": odds_data.get("sportsbook"),
            "fair_probabilities": fair_p,
            "original_odds": moneyline,
            "analysis": f"Computed fair probabilities from {odds_data.get('sportsbook')} odds"
        }


class ForecastEvaluatorAgent(Agent):
    """Agent responsible for evaluating predictive model forecasts"""
    
    def __init__(self, name: str = "ForecastEvaluator"):
        super().__init__(name=name)
        self.expertise = "Evaluating and validating model forecasts"
    
    def evaluate_forecast(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate forecast data for validity and extract predictions
        
        Args:
            forecast_data: Dictionary containing model predictions
            
        Returns:
            Dictionary with validated forecast
        """
        p_model = forecast_data.get("p_model", {})
        home_p = p_model.get("home")
        away_p = p_model.get("away")
        
        if home_p is None or away_p is None:
            raise ValueError("Invalid forecast data")
        
        # Validate probabilities sum to approximately 1
        total = home_p + away_p
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Forecast probabilities don't sum to 1.0: {total}")
        
        confidence = abs(home_p - away_p)  # Higher difference = more confident
        
        return {
            "event_id": forecast_data.get("event_id"),
            "model_probabilities": p_model,
            "confidence": confidence,
            "prediction": "home" if home_p > away_p else "away",
            "analysis": f"Model predicts {('home' if home_p > away_p else 'away')} "
                       f"with {confidence:.1%} confidence margin"
        }


class EdgeCalculatorAgent(Agent):
    """Agent responsible for calculating betting edges"""
    
    def __init__(self, name: str = "EdgeCalculator"):
        super().__init__(name=name)
        self.expertise = "Computing betting edges and identifying value opportunities"
    
    def calculate_edge(self, fair_p: Dict[str, float], model_p: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate betting edge by comparing model predictions to fair odds
        
        Args:
            fair_p: Fair probabilities from odds analysis
            model_p: Model predicted probabilities
            
        Returns:
            Dictionary with edge calculations
        """
        e = edge(model_p, fair_p)
        
        # Determine if there's a betting opportunity (edge > threshold)
        threshold = 0.02  # 2% edge required
        opportunities = []
        
        for side in ["home", "away"]:
            if e[side] > threshold:
                opportunities.append({
                    "side": side,
                    "edge": e[side],
                    "edge_pct": e[side] * 100,
                    "recommendation": "BET",
                    "confidence": "HIGH" if e[side] > 0.05 else "MEDIUM"
                })
            elif e[side] < -threshold:
                opportunities.append({
                    "side": side,
                    "edge": e[side],
                    "edge_pct": e[side] * 100,
                    "recommendation": "AVOID",
                    "confidence": "HIGH"
                })
        
        return {
            "edge": e,
            "edge_pct": {k: round(100.0 * v, 2) for k, v in e.items()},
            "opportunities": opportunities,
            "has_positive_edge": any(e[side] > threshold for side in ["home", "away"]),
            "analysis": self._generate_edge_analysis(e, opportunities)
        }
    
    def _generate_edge_analysis(self, edges: Dict[str, float], opportunities: List[Dict]) -> str:
        """Generate human-readable analysis of the edge"""
        if not opportunities:
            return "No significant betting edge found. Pass on this game."
        
        analyses = []
        for opp in opportunities:
            if opp["recommendation"] == "BET":
                analyses.append(
                    f"{opp['side'].upper()}: {opp['edge_pct']:.2f}% edge - "
                    f"{opp['confidence']} confidence bet opportunity"
                )
            else:
                analyses.append(
                    f"{opp['side'].upper()}: {opp['edge_pct']:.2f}% negative edge - AVOID"
                )
        
        return " | ".join(analyses)


class ReportGeneratorAgent(Agent):
    """Agent responsible for generating final reports"""
    
    def __init__(self, name: str = "ReportGenerator"):
        super().__init__(name=name)
        self.expertise = "Synthesizing analysis into actionable reports"
    
    def generate_report(self, 
                       odds_analysis: Dict[str, Any],
                       forecast_eval: Dict[str, Any],
                       edge_calc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive betting edge report
        
        Args:
            odds_analysis: Output from OddsAnalyzerAgent
            forecast_eval: Output from ForecastEvaluatorAgent
            edge_calc: Output from EdgeCalculatorAgent
            
        Returns:
            Complete report dictionary
        """
        event_id = odds_analysis.get("event_id")
        fair_p = odds_analysis.get("fair_probabilities")
        model_p = forecast_eval.get("model_probabilities")
        
        # Build detailed edge reports
        reports = build_edge_reports(
            event_id=event_id,
            sportsbook=odds_analysis.get("sportsbook"),
            fair_p=fair_p,
            model_p=model_p
        )
        
        # Compile final report
        final_report = {
            "event_id": event_id,
            "sport": odds_analysis.get("sport"),
            "league": odds_analysis.get("league"),
            "matchup": {
                "home": odds_analysis.get("home_team"),
                "away": odds_analysis.get("away_team")
            },
            "sportsbook": odds_analysis.get("sportsbook"),
            "original_odds": odds_analysis.get("original_odds"),
            "fair_probabilities": {k: round(v, 4) for k, v in fair_p.items()},
            "model_probabilities": {k: round(v, 4) for k, v in model_p.items()},
            "edge_analysis": edge_calc,
            "model_prediction": forecast_eval.get("prediction"),
            "model_confidence": round(forecast_eval.get("confidence", 0), 4),
            "detailed_reports": as_jsonable(reports),
            "recommendation": self._generate_recommendation(edge_calc),
            "agent_analyses": {
                "odds": odds_analysis.get("analysis"),
                "forecast": forecast_eval.get("analysis"),
                "edge": edge_calc.get("analysis")
            }
        }
        
        return final_report
    
    def _generate_recommendation(self, edge_calc: Dict[str, Any]) -> str:
        """Generate final betting recommendation"""
        if edge_calc.get("has_positive_edge"):
            opportunities = edge_calc.get("opportunities", [])
            bet_opps = [o for o in opportunities if o["recommendation"] == "BET"]
            if bet_opps:
                best_opp = max(bet_opps, key=lambda x: x["edge"])
                return (f"RECOMMENDED BET: {best_opp['side'].upper()} - "
                       f"{best_opp['edge_pct']:.2f}% edge ({best_opp['confidence']} confidence)")
        
        return "NO BET RECOMMENDED - No significant edge detected"


class SportsEdgeFlow(Flow):
    """
    Multi-agent workflow for sports betting edge analysis
    Coordinates multiple specialized agents to analyze betting opportunities
    """
    
    def __init__(self):
        super().__init__(name="SportsEdgeAnalysis")
        
        # Initialize specialized agents
        self.odds_agent = OddsAnalyzerAgent()
        self.forecast_agent = ForecastEvaluatorAgent()
        self.edge_agent = EdgeCalculatorAgent()
        self.report_agent = ReportGeneratorAgent()
        
        self.agents = [
            self.odds_agent,
            self.forecast_agent,
            self.edge_agent,
            self.report_agent
        ]
    
    def run(self, odds_data: Dict[str, Any], forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the full agentic workflow
        
        Args:
            odds_data: Sportsbook odds data
            forecast_data: Model forecast data
            
        Returns:
            Complete analysis report
        """
        # Task 1: Analyze odds
        odds_analysis = self.odds_agent.analyze_odds(odds_data)
        
        # Task 2: Evaluate forecast
        forecast_eval = self.forecast_agent.evaluate_forecast(forecast_data)
        
        # Task 3: Calculate edge
        edge_calc = self.edge_agent.calculate_edge(
            fair_p=odds_analysis["fair_probabilities"],
            model_p=forecast_eval["model_probabilities"]
        )
        
        # Task 4: Generate report
        final_report = self.report_agent.generate_report(
            odds_analysis=odds_analysis,
            forecast_eval=forecast_eval,
            edge_calc=edge_calc
        )
        
        return final_report
    
    def run_batch(self, games: List[tuple[Dict[str, Any], Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Process multiple games in batch
        
        Args:
            games: List of (odds_data, forecast_data) tuples
            
        Returns:
            List of analysis reports
        """
        reports = []
        for odds_data, forecast_data in games:
            try:
                report = self.run(odds_data, forecast_data)
                reports.append(report)
            except Exception as e:
                print(f"Error processing game {odds_data.get('event_id')}: {e}")
                continue
        
        return reports