"""
LLM-Powered Agentic Workflow for Sports Edge Analysis
Uses Phi-3-mini for agent reasoning and decision-making
"""
from __future__ import annotations
from typing import Dict, Any, List
import json

from .fair_framework import Agent, Flow, LLMConfig
from .probability_calc import fair_probs_from_moneyline
from .probability_adjuster import edge
from .report_formatter import build_edge_reports, as_jsonable


class LLMOddsAnalyzerAgent(Agent):
    """LLM-powered agent for analyzing sportsbook odds"""
    
    def __init__(self):
        super().__init__("OddsAnalyzer", model_name=LLMConfig.PHI3_MINI)
        self.expertise = "Analyzing sportsbook odds and calculating fair probabilities using mathematical models"
        self.system_prompt = """You are an expert sports betting analyst specializing in odds analysis.
Your task is to analyze sportsbook odds and explain the concept of 'vig' (vigorish).
Always provide clear, concise explanations of the mathematical reasoning."""
    
    def _fallback_response(self, prompt: str) -> str:
        """Rule-based fallback when LLM unavailable"""
        return "Analyzed odds and removed vig using standard mathematical formulas."
    
    def run(self, odds_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze odds using LLM reasoning combined with mathematical calculation
        
        Args:
            odds_data: Dictionary containing sportsbook odds information
            
        Returns:
            Dictionary with fair probabilities and LLM analysis
        """
        home_ml = odds_data.get('moneyline', {}).get('home')
        away_ml = odds_data.get('moneyline', {}).get('away')
        
        # Calculate fair probabilities mathematically
        fair_p = fair_probs_from_moneyline(home_ml, away_ml)
        
        # Use LLM to provide reasoning and explanation
        llm_prompt = f"""Analyze these sportsbook odds:
- {odds_data.get('home_team')}: {home_ml}
- {odds_data.get('away_team')}: {away_ml}
- Sportsbook: {odds_data.get('sportsbook')}

The fair probabilities after removing vig are:
- {odds_data.get('home_team')}: {fair_p['home']:.1%}
- {odds_data.get('away_team')}: {fair_p['away']:.1%}

Explain in 1-2 sentences why removing the vig is important for finding betting value."""
        
        llm_analysis = self.invoke_llm(llm_prompt, max_tokens=150)
        
        return {
            "event_id": odds_data.get("event_id"),
            "sportsbook": odds_data.get("sportsbook"),
            "original_odds": {"home": home_ml, "away": away_ml},
            "fair_probabilities": fair_p,
            "analysis": llm_analysis,
            "agent": self.name
        }


class LLMForecastEvaluatorAgent(Agent):
    """LLM-powered agent for evaluating model forecasts"""
    
    def __init__(self):
        super().__init__("ForecastEvaluator", model_name=LLMConfig.PHI3_MINI)
        self.expertise = "Evaluating and validating sports prediction models"
        self.system_prompt = """You are a sports forecasting expert who evaluates prediction models.
Your task is to assess the quality and reasonableness of probability forecasts.
Provide brief, insightful commentary on forecast quality."""
    
    def _fallback_response(self, prompt: str) -> str:
        return "Forecast validated. Probabilities sum to 100% and are within valid ranges."
    
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate forecast using LLM reasoning
        
        Args:
            data: Combined odds analysis and forecast data
            
        Returns:
            Data with LLM evaluation added
        """
        odds_analysis, forecast_data = data['odds_analysis'], data['forecast']
        
        model_p = forecast_data.get("p_model", {})
        
        # Validation checks
        prob_sum = model_p.get('home', 0) + model_p.get('away', 0)
        is_valid = abs(prob_sum - 1.0) < 0.01 and all(0 <= p <= 1 for p in model_p.values())
        
        # LLM evaluation
        llm_prompt = f"""Evaluate this sports prediction forecast:
- Model predicts: Home {model_p.get('home', 0):.1%}, Away {model_p.get('away', 0):.1%}
- Fair market odds: Home {odds_analysis['fair_probabilities']['home']:.1%}, Away {odds_analysis['fair_probabilities']['away']:.1%}
- Validation: {'PASSED' if is_valid else 'FAILED'}

In 1-2 sentences, assess whether this forecast appears reasonable and if there's significant disagreement with the market."""
        
        llm_evaluation = self.invoke_llm(llm_prompt, max_tokens=150)
        
        return {
            **odds_analysis,
            "model_probabilities": model_p,
            "forecast_validation": {
                "is_valid": is_valid,
                "llm_evaluation": llm_evaluation
            },
            "agent": self.name
        }


class LLMEdgeCalculatorAgent(Agent):
    """LLM-powered agent for calculating betting edges"""
    
    def __init__(self):
        super().__init__("EdgeCalculator", model_name=LLMConfig.PHI3_MINI)
        self.expertise = "Calculating betting edges and identifying value opportunities"
        self.system_prompt = """You are a professional sports bettor specializing in edge calculation.
Your task is to identify valuable betting opportunities by comparing model predictions to market odds.
Provide clear insights on edge magnitude and opportunity quality."""
    
    def _fallback_response(self, prompt: str) -> str:
        return "Edge calculated. Positive edges indicate potential betting value."
    
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate edge using LLM reasoning
        
        Args:
            data: Combined analysis with odds and forecast
            
        Returns:
            Data with edge analysis and LLM insights
        """
        fair_p = data.get("fair_probabilities")
        model_p = data.get("model_probabilities")
        
        # Calculate mathematical edge
        e = edge(model_p, fair_p)
        
        home_edge = e['home']
        away_edge = e['away']
        max_edge = max(home_edge, away_edge)
        
        # LLM analysis of edge
        llm_prompt = f"""Analyze this betting edge:
- Home team edge: {home_edge:+.2f}%
- Away team edge: {away_edge:+.2f}%
- Maximum edge: {max_edge:.2f}%

Professional bettors typically look for edges above 2%.

In 2-3 sentences, assess: (1) Is this a strong betting opportunity? (2) Which side has value? (3) What's your confidence level?"""
        
        llm_insight = self.invoke_llm(llm_prompt, max_tokens=200)
        
        return {
            **data,
            "edge_analysis": {
                "edge_pct": {"home": home_edge, "away": away_edge},
                "has_positive_edge": max_edge > 0,
                "max_edge": max_edge,
                "llm_insight": llm_insight
            },
            "agent": self.name
        }


class LLMReportGeneratorAgent(Agent):
    """LLM-powered agent for generating betting recommendations"""
    
    def __init__(self):
        super().__init__("ReportGenerator", model_name=LLMConfig.PHI3_MINI)
        self.expertise = "Generating actionable betting recommendations with clear reasoning"
        self.system_prompt = """You are a professional betting advisor who makes clear, actionable recommendations.
Your task is to synthesize edge analysis into betting decisions.
Always explain your reasoning clearly and state confidence levels."""
    
    def _fallback_response(self, prompt: str) -> str:
        return "Recommendation generated based on edge thresholds and risk management."
    
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recommendation using LLM reasoning
        
        Args:
            data: Complete analysis with edges
            
        Returns:
            Final report with LLM-powered recommendation
        """
        edge_analysis = data.get("edge_analysis", {})
        edge_pct = edge_analysis.get("edge_pct", {})
        
        home_edge = edge_pct.get('home', 0)
        away_edge = edge_pct.get('away', 0)
        
        # Determine best opportunity
        if home_edge > away_edge and home_edge > 2.0:
            recommended_side = "HOME"
            recommended_edge = home_edge
        elif away_edge > 2.0:
            recommended_side = "AWAY"
            recommended_edge = away_edge
        else:
            recommended_side = None
            recommended_edge = max(home_edge, away_edge)
        
        # LLM generates final recommendation
        if recommended_side:
            llm_prompt = f"""Generate a betting recommendation:
- Recommended side: {recommended_side}
- Edge: {recommended_edge:.2f}%
- Context: Edge > 2% is our threshold for betting
- Confidence levels: 2-5% = MEDIUM, 5%+ = HIGH

Write a concise recommendation in this format: "RECOMMENDED BET: [SIDE] - [EDGE]% edge ([CONFIDENCE] confidence)"
Then add one sentence explaining the reasoning."""
        else:
            llm_prompt = f"""Generate a PASS recommendation:
- Best edge available: {recommended_edge:.2f}%
- Threshold: We need 2%+ edge to bet
- Current situation: No edge meets our criteria

Write: "PASS - No edges above 2% threshold" then explain why in one sentence."""
        
        llm_recommendation = self.invoke_llm(llm_prompt, max_tokens=150)
        
        # Build final report using correct function signature
        edge_reports = build_edge_reports(
            event_id=data.get("event_id"),
            sportsbook=data.get("sportsbook"),
            fair_p=data.get("fair_probabilities"),
            model_p=data.get("model_probabilities")
        )
        
        # Convert to dict format
        report = {
            "event_id": data.get("event_id"),
            "sport": data.get("sport", "unknown"),
            "league": data.get("league", "unknown"),
            "sportsbook": data.get("sportsbook"),
            "matchup": {
                "home": data.get("home_team", "Home"),
                "away": data.get("away_team", "Away")
            },
            "original_odds": data.get("original_odds"),
            "fair_probabilities": data.get("fair_probabilities"),
            "model_probabilities": data.get("model_probabilities"),
            "edge_analysis": {
                "edge_pct": edge_pct,
                "has_positive_edge": max(edge_pct.values()) > 0,
                "opportunities": as_jsonable(edge_reports)
            }
        }
        
        # Add LLM recommendation
        report['llm_recommendation'] = llm_recommendation
        report['recommendation'] = llm_recommendation.split('\n')[0] if '\n' in llm_recommendation else llm_recommendation
        
        # Add all LLM insights from previous agents
        report['llm_insights'] = {
            'odds_analysis': data.get('analysis', ''),
            'forecast_evaluation': data.get('forecast_validation', {}).get('llm_evaluation', ''),
            'edge_insight': edge_analysis.get('llm_insight', ''),
            'final_recommendation': llm_recommendation
        }
        
        return report


class LLMSportsEdgeFlow(Flow):
    """
    Main flow coordinator using LLM-powered agents
    """
    
    def __init__(self):
        super().__init__("LLM-SportsEdgeFlow")
        
        # Initialize LLM-powered agents
        self.odds_analyzer = LLMOddsAnalyzerAgent()
        self.forecast_evaluator = LLMForecastEvaluatorAgent()
        self.edge_calculator = LLMEdgeCalculatorAgent()
        self.report_generator = LLMReportGeneratorAgent()
        
        # Add to flow
        self.agents = [
            self.odds_analyzer,
            self.forecast_evaluator,
            self.edge_calculator,
            self.report_generator
        ]
    
    def run(self, odds_data: Dict[str, Any], forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the LLM-powered agentic workflow
        
        Args:
            odds_data: Sportsbook odds information
            forecast_data: Model predictions
            
        Returns:
            Complete analysis report with LLM insights
        """
        print(f"\n{'='*70}")
        print(f"[{self.name}] Starting LLM-powered analysis...")
        print(f"{'='*70}\n")
        
        # Step 1: Analyze odds with LLM
        odds_analysis = self.odds_analyzer.run(odds_data)
        
        # Step 2: Evaluate forecast with LLM
        combined_data = {
            'odds_analysis': odds_analysis,
            'forecast': forecast_data
        }
        evaluated_data = self.forecast_evaluator.run(combined_data)
        
        # Step 3: Calculate edge with LLM insights
        edge_data = self.edge_calculator.run(evaluated_data)
        
        # Add original data fields needed by report generator
        edge_data['sport'] = odds_data.get('sport', 'unknown')
        edge_data['league'] = odds_data.get('league', 'unknown')
        edge_data['home_team'] = odds_data.get('home_team', 'Home')
        edge_data['away_team'] = odds_data.get('away_team', 'Away')
        
        # Step 4: Generate recommendation with LLM
        final_report = self.report_generator.run(edge_data)
        
        print(f"\n[{self.name}] Analysis complete!")
        print(f"{'='*70}\n")
        
        return final_report


# Keep backward compatibility with original implementation
SportsEdgeFlow = LLMSportsEdgeFlow


if __name__ == "__main__":
    # Test the LLM-powered workflow
    print("Testing LLM-powered Sports Edge Analysis...\n")
    
    workflow = LLMSportsEdgeFlow()
    
    # Test data
    odds = {
        "event_id": "test-llm-001",
        "sport": "basketball",
        "league": "NBA",
        "home_team": "Lakers",
        "away_team": "Celtics",
        "sportsbook": "DraftKings",
        "moneyline": {"home": -150, "away": +130}
    }
    
    forecast = {
        "event_id": "test-llm-001",
        "p_model": {"home": 0.65, "away": 0.35}
    }
    
    report = workflow.run(odds, forecast)
    
    print("\n" + "="*70)
    print("FINAL REPORT WITH LLM INSIGHTS")
    print("="*70)
    print(json.dumps(report, indent=2, default=str))
