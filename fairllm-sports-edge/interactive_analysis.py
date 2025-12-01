#!/usr/bin/env python3
"""
Interactive Sports Edge Analysis
Chat with the multi-agent system!
"""
import sys
sys.path.insert(0, 'src')

import json
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from fairllm_agent.agentic_workflow import SportsEdgeFlow

console = Console()

def get_odds_from_user():
    """Get odds input from user"""
    console.print("\n[bold cyan]Enter Game Information[/bold cyan]\n")
    
    event_id = Prompt.ask("Event ID (e.g., 2025-12-01-NBA-001)")
    sport = Prompt.ask("Sport", default="basketball")
    league = Prompt.ask("League", default="NBA")
    home_team = Prompt.ask("Home Team")
    away_team = Prompt.ask("Away Team")
    sportsbook = Prompt.ask("Sportsbook", default="DraftKings")
    
    console.print("\n[yellow]Enter American odds (e.g., -150 for favorite, +130 for underdog)[/yellow]")
    home_odds = IntPrompt.ask(f"{home_team} odds")
    away_odds = IntPrompt.ask(f"{away_team} odds")
    
    return {
        "event_id": event_id,
        "sport": sport,
        "league": league,
        "home_team": home_team,
        "away_team": away_team,
        "sportsbook": sportsbook,
        "moneyline": {
            "home": home_odds,
            "away": away_odds
        }
    }

def get_forecast_from_user(event_id):
    """Get model forecast from user"""
    console.print("\n[bold cyan]Enter Model Prediction[/bold cyan]\n")
    console.print("[yellow]Probabilities should sum to 1.0 (e.g., 0.62 and 0.38)[/yellow]")
    
    home_prob = float(Prompt.ask("Home team win probability (0.0 to 1.0)"))
    away_prob = 1.0 - home_prob
    
    console.print(f"[dim]Away probability calculated as: {away_prob:.2f}[/dim]")
    
    return {
        "event_id": event_id,
        "p_model": {
            "home": home_prob,
            "away": away_prob
        }
    }

def display_report(report):
    """Display analysis report"""
    console.print("\n" + "="*70)
    console.print("[bold]ANALYSIS RESULTS[/bold]")
    console.print("="*70 + "\n")
    
    console.print(f"[yellow]Event:[/yellow] {report['event_id']}")
    console.print(f"[yellow]Matchup:[/yellow] {report['matchup']['home']} vs {report['matchup']['away']}")
    console.print(f"[yellow]Sportsbook:[/yellow] {report['sportsbook']}\n")
    
    console.print(f"[cyan]Original Odds:[/cyan]")
    console.print(f"  {report['matchup']['home']}: {report['original_odds']['home']:+d}")
    console.print(f"  {report['matchup']['away']}: {report['original_odds']['away']:+d}\n")
    
    console.print(f"[cyan]Fair Probabilities (vig removed):[/cyan]")
    console.print(f"  {report['matchup']['home']}: {report['fair_probabilities']['home']:.2%}")
    console.print(f"  {report['matchup']['away']}: {report['fair_probabilities']['away']:.2%}\n")
    
    console.print(f"[cyan]Model Predictions:[/cyan]")
    console.print(f"  {report['matchup']['home']}: {report['model_probabilities']['home']:.2%}")
    console.print(f"  {report['matchup']['away']}: {report['model_probabilities']['away']:.2%}\n")
    
    console.print(f"[cyan]Betting Edge:[/cyan]")
    for side in ['home', 'away']:
        team = report['matchup'][side]
        edge = report['edge_analysis']['edge_pct'][side]
        color = "green" if edge > 0 else "red"
        console.print(f"  {team}: [{color}]{edge:+.2f}%[/{color}]")
    
    console.print()
    if "RECOMMENDED BET" in report['recommendation']:
        console.print(Panel(report['recommendation'], style="bold green", title="💰 RECOMMENDATION"))
    else:
        console.print(Panel(report['recommendation'], style="bold yellow", title="⚠️  RECOMMENDATION"))
    
    console.print(f"\n[bold]Agent Analyses:[/bold]")
    for agent, analysis in report['agent_analyses'].items():
        console.print(f"  [cyan]{agent.title()}:[/cyan] {analysis}")

def main():
    console.print(Panel.fit(
        "[bold magenta]Interactive Sports Edge Analysis[/bold magenta]\n"
        "Multi-Agent Betting Edge Calculator",
        border_style="magenta"
    ))
    
    workflow = SportsEdgeFlow()
    console.print("\n[green]✓ Multi-agent workflow initialized[/green]")
    console.print(f"[green]✓ Agents loaded:[/green] {', '.join([a.name for a in workflow.agents])}\n")
    
    while True:
        try:
            odds_data = get_odds_from_user()
            forecast_data = get_forecast_from_user(odds_data['event_id'])
            
            console.print("\n[yellow]Running multi-agent analysis...[/yellow]")
            report = workflow.run(odds_data, forecast_data)
            
            display_report(report)
            
            console.print()
            if not Prompt.ask("\nAnalyze another game?", choices=["y", "n"], default="y") == "y":
                break
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            if not Prompt.ask("\nTry again?", choices=["y", "n"], default="y") == "y":
                break
    
    console.print("\n[cyan]Thank you for using Sports Edge Analysis![/cyan]\n")

if __name__ == "__main__":
    main()
