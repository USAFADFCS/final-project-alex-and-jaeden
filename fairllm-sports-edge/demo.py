#!/usr/bin/env python3
"""
Demo script showing the FairLLM Sports Edge Analysis system
Demonstrates the full agentic workflow with clear output
"""
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from fairllm_agent.agentic_workflow import SportsEdgeFlow

console = Console()


def print_section(title: str):
    """Print a section header"""
    console.print(f"\n[bold cyan]{'='*70}[/bold cyan]")
    console.print(f"[bold white]{title}[/bold white]")
    console.print(f"[bold cyan]{'='*70}[/bold cyan]\n")


def demo_single_game():
    """Demonstrate analysis of a single game"""
    print_section("DEMO 1: Single Game Analysis")
    
    # Sample data
    odds_data = {
        "event_id": "2025-11-25-NBA-001",
        "sport": "basketball",
        "league": "NBA",
        "home_team": "Los Angeles Lakers",
        "away_team": "Boston Celtics",
        "sportsbook": "DraftKings",
        "moneyline": {"home": -150, "away": 130}
    }
    
    forecast_data = {
        "event_id": "2025-11-25-NBA-001",
        "p_model": {"home": 0.62, "away": 0.38}
    }
    
    console.print("[yellow]Game:[/yellow] Lakers (Home) vs Celtics (Away)")
    console.print(f"[yellow]Odds:[/yellow] Lakers {odds_data['moneyline']['home']}, Celtics {odds_data['moneyline']['away']}")
    console.print(f"[yellow]Model Prediction:[/yellow] Lakers {forecast_data['p_model']['home']:.1%}, Celtics {forecast_data['p_model']['away']:.1%}\n")
    
    console.print("[cyan]Initializing multi-agent workflow...[/cyan]")
    workflow = SportsEdgeFlow()
    
    console.print("[cyan]Agents loaded:[/cyan]")
    console.print("  • OddsAnalyzerAgent")
    console.print("  • ForecastEvaluatorAgent")
    console.print("  • EdgeCalculatorAgent")
    console.print("  • ReportGeneratorAgent\n")
    
    console.print("[yellow]Running analysis pipeline...[/yellow]\n")
    
    # Run workflow
    report = workflow.run(odds_data, forecast_data)
    
    # Display results
    console.print("[green]Analysis Complete![/green]\n")
    
    console.print(f"[yellow]Fair Probabilities (vig removed):[/yellow]")
    console.print(f"  Lakers: {report['fair_probabilities']['home']:.2%}")
    console.print(f"  Celtics: {report['fair_probabilities']['away']:.2%}\n")
    
    console.print(f"[yellow]Edge Analysis:[/yellow]")
    for side in ['home', 'away']:
        team = odds_data['home_team'] if side == 'home' else odds_data['away_team']
        edge_pct = report['edge_analysis']['edge_pct'][side]
        color = "green" if edge_pct > 0 else "red"
        console.print(f"  {team}: [{color}]{edge_pct:+.2f}%[/{color}]")
    
    console.print(f"\n[bold]Final Recommendation:[/bold]")
    console.print(Panel(report['recommendation'], style="bold green"))
    
    return report


def demo_batch_processing():
    """Demonstrate batch processing of multiple games"""
    print_section("DEMO 2: Batch Processing (5 Games)")
    
    games = [
        (
            {
                "event_id": "2025-11-25-NBA-001",
                "sport": "basketball",
                "league": "NBA",
                "home_team": "Los Angeles Lakers",
                "away_team": "Boston Celtics",
                "sportsbook": "DraftKings",
                "moneyline": {"home": -150, "away": 130}
            },
            {
                "event_id": "2025-11-25-NBA-001",
                "p_model": {"home": 0.62, "away": 0.38}
            }
        ),
        (
            {
                "event_id": "2025-11-25-NBA-002",
                "sport": "basketball",
                "league": "NBA",
                "home_team": "Golden State Warriors",
                "away_team": "Phoenix Suns",
                "sportsbook": "FanDuel",
                "moneyline": {"home": -110, "away": -110}
            },
            {
                "event_id": "2025-11-25-NBA-002",
                "p_model": {"home": 0.48, "away": 0.52}
            }
        ),
        (
            {
                "event_id": "2025-11-25-NFL-001",
                "sport": "football",
                "league": "NFL",
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "sportsbook": "BetMGM",
                "moneyline": {"home": -180, "away": 155}
            },
            {
                "event_id": "2025-11-25-NFL-001",
                "p_model": {"home": 0.68, "away": 0.32}
            }
        ),
        (
            {
                "event_id": "2025-11-25-NHL-001",
                "sport": "hockey",
                "league": "NHL",
                "home_team": "Colorado Avalanche",
                "away_team": "Vegas Golden Knights",
                "sportsbook": "Caesars",
                "moneyline": {"home": 120, "away": -140}
            },
            {
                "event_id": "2025-11-25-NHL-001",
                "p_model": {"home": 0.52, "away": 0.48}
            }
        ),
        (
            {
                "event_id": "2025-11-25-NBA-003",
                "sport": "basketball",
                "league": "NBA",
                "home_team": "Miami Heat",
                "away_team": "Milwaukee Bucks",
                "sportsbook": "DraftKings",
                "moneyline": {"home": 145, "away": -165}
            },
            {
                "event_id": "2025-11-25-NBA-003",
                "p_model": {"home": 0.43, "away": 0.57}
            }
        )
    ]
    
    console.print("[cyan]Processing 5 games across NBA, NFL, and NHL...[/cyan]\n")
    
    workflow = SportsEdgeFlow()
    reports = workflow.run_batch(games)
    
    console.print(f"[green]Batch processing complete![/green]\n")
    console.print(f"[yellow]Summary:[/yellow]")
    console.print(f"  Total games analyzed: {len(reports)}")
    
    bet_count = sum(1 for r in reports if "RECOMMENDED BET" in r['recommendation'])
    console.print(f"  Recommended bets: {bet_count}")
    console.print(f"  Pass recommendations: {len(reports) - bet_count}\n")
    
    console.print("[yellow]Top Opportunities:[/yellow]")
    
    # Sort by max edge
    sorted_reports = sorted(
        reports,
        key=lambda r: max(r['edge_analysis']['edge_pct']['home'], 
                         r['edge_analysis']['edge_pct']['away']),
        reverse=True
    )
    
    for i, report in enumerate(sorted_reports[:3], 1):
        matchup = f"{report['matchup']['home']} vs {report['matchup']['away']}"
        edge_pct = report['edge_analysis']['edge_pct']
        best_edge = max(edge_pct['home'], edge_pct['away'])
        console.print(f"  {i}. {matchup} - {best_edge:+.2f}% edge")
    
    return reports


def demo_agent_insights():
    """Show detailed agent-by-agent analysis"""
    print_section("DEMO 3: Agent-by-Agent Analysis")
    
    odds_data = {
        "event_id": "DEMO-GAME",
        "sport": "basketball",
        "league": "NBA",
        "home_team": "Team A",
        "away_team": "Team B",
        "sportsbook": "DemoBook",
        "moneyline": {"home": -110, "away": -110}
    }
    
    forecast_data = {
        "event_id": "DEMO-GAME",
        "p_model": {"home": 0.55, "away": 0.45}
    }
    
    workflow = SportsEdgeFlow()
    
    # Step through each agent
    console.print("[bold]Step 1: OddsAnalyzerAgent[/bold]")
    odds_analysis = workflow.odds_agent.analyze_odds(odds_data)
    console.print(f"  Input: Home {odds_data['moneyline']['home']}, Away {odds_data['moneyline']['away']}")
    console.print(f"  Output: Fair probabilities")
    console.print(f"    Home: {odds_analysis['fair_probabilities']['home']:.4f}")
    console.print(f"    Away: {odds_analysis['fair_probabilities']['away']:.4f}")
    console.print(f"  [cyan]{odds_analysis['analysis']}[/cyan]\n")
    
    console.print("[bold]Step 2: ForecastEvaluatorAgent[/bold]")
    forecast_eval = workflow.forecast_agent.evaluate_forecast(forecast_data)
    console.print(f"  Input: Model predictions (Home: {forecast_data['p_model']['home']}, Away: {forecast_data['p_model']['away']})")
    console.print(f"  Output: Validated forecast")
    console.print(f"    Prediction: {forecast_eval['prediction'].upper()}")
    console.print(f"    Confidence Margin: {forecast_eval['confidence']:.1%}")
    console.print(f"  [cyan]{forecast_eval['analysis']}[/cyan]\n")
    
    console.print("[bold]Step 3: EdgeCalculatorAgent[/bold]")
    edge_calc = workflow.edge_agent.calculate_edge(
        odds_analysis['fair_probabilities'],
        forecast_eval['model_probabilities']
    )
    console.print(f"  Input: Fair probs vs Model probs")
    console.print(f"  Output: Edge calculations")
    console.print(f"    Home Edge: {edge_calc['edge_pct']['home']:+.2f}%")
    console.print(f"    Away Edge: {edge_calc['edge_pct']['away']:+.2f}%")
    console.print(f"  [cyan]{edge_calc['analysis']}[/cyan]\n")
    
    console.print("[bold]Step 4: ReportGeneratorAgent[/bold]")
    report = workflow.report_agent.generate_report(
        odds_analysis, forecast_eval, edge_calc
    )
    console.print(f"  Input: All agent outputs")
    console.print(f"  Output: Final recommendation")
    console.print(f"    [green]{report['recommendation']}[/green]\n")


def main():
    """Run all demos"""
    console.print("\n[bold magenta]╔═══════════════════════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║   FairLLM Sports Edge Analysis - System Demonstration    ║[/bold magenta]")
    console.print("[bold magenta]║          Multi-Agent Betting Edge Calculator             ║[/bold magenta]")
    console.print("[bold magenta]╚═══════════════════════════════════════════════════════════╝[/bold magenta]\n")
    
    # Demo 1
    demo_single_game()
    input("\nPress Enter to continue to Demo 2...")
    
    # Demo 2
    demo_batch_processing()
    input("\nPress Enter to continue to Demo 3...")
    
    # Demo 3
    demo_agent_insights()
    
    print_section("Demo Complete")
    console.print("[green]All demonstrations completed successfully![/green]")
    console.print("\n[yellow]Key Takeaways:[/yellow]")
    console.print("  • Four specialized agents work together seamlessly")
    console.print("  • System handles multiple sports and bet types")
    console.print("  • Batch processing enables efficient analysis")
    console.print("  • Clear, actionable recommendations with confidence levels")
    console.print("\n[cyan]For more information, see README_COMPLETE.md[/cyan]\n")


if __name__ == "__main__":
    main()