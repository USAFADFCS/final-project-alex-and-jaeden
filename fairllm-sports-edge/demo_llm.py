#!/usr/bin/env python3
"""
Demo: LLM-Powered Sports Edge Analysis with Phi-3-mini
Shows how agents use LLMs for reasoning and decision-making
"""
import sys
sys.path.insert(0, 'src')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import the LLM version
from fairllm_agent.agentic_workflow_llm import LLMSportsEdgeFlow

console = Console()

def main():
    console.print(Panel.fit(
        "[bold magenta]LLM-Powered Sports Edge Analysis[/bold magenta]\n"
        "Using Phi-3-mini for Agent Reasoning",
        border_style="magenta"
    ))
    
    console.print("\n[cyan]Initializing LLM-powered agents...[/cyan]")
    workflow = LLMSportsEdgeFlow()
    
    console.print(f"[green]✓ Loaded {len(workflow.agents)} LLM-powered agents[/green]\n")
    
    # Demo game
    console.print("[bold yellow]Demo Game: Lakers vs Celtics[/bold yellow]\n")
    
    odds_data = {
        "event_id": "2025-12-02-NBA-001",
        "sport": "basketball",
        "league": "NBA",
        "home_team": "Los Angeles Lakers",
        "away_team": "Boston Celtics",
        "sportsbook": "DraftKings",
        "moneyline": {"home": -140, "away": +120}
    }
    
    forecast_data = {
        "event_id": "2025-12-02-NBA-001",
        "p_model": {"home": 0.62, "away": 0.38}
    }
    
    console.print("[dim]Input Odds:[/dim]")
    console.print(f"  Lakers: -140")
    console.print(f"  Celtics: +120")
    console.print(f"  Sportsbook: DraftKings\n")
    
    console.print("[dim]Model Forecast:[/dim]")
    console.print(f"  Lakers: 62%")
    console.print(f"  Celtics: 38%\n")
    
    console.print("[yellow]Running LLM-powered analysis...[/yellow]\n")
    
    # Run workflow
    report = workflow.run(odds_data, forecast_data)
    
    # Display results
    console.print("\n" + "="*70)
    console.print("[bold]RESULTS WITH LLM REASONING[/bold]")
    console.print("="*70 + "\n")
    
    # Show LLM insights from each agent
    if 'llm_insights' in report:
        insights = report['llm_insights']
        
        console.print(Panel(
            insights.get('odds_analysis', 'N/A'),
            title="[cyan]🤖 OddsAnalyzer LLM Reasoning[/cyan]",
            border_style="cyan"
        ))
        
        console.print(Panel(
            insights.get('forecast_evaluation', 'N/A'),
            title="[cyan]🤖 ForecastEvaluator LLM Reasoning[/cyan]",
            border_style="cyan"
        ))
        
        console.print(Panel(
            insights.get('edge_insight', 'N/A'),
            title="[cyan]🤖 EdgeCalculator LLM Reasoning[/cyan]",
            border_style="cyan"
        ))
        
        console.print(Panel(
            insights.get('final_recommendation', 'N/A'),
            title="[cyan]🤖 ReportGenerator LLM Reasoning[/cyan]",
            border_style="cyan"
        ))
    
    # Show final numbers
    console.print("\n[bold]Mathematical Results:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric")
    table.add_column("Lakers", justify="right")
    table.add_column("Celtics", justify="right")
    
    table.add_row(
        "Fair Probability",
        f"{report['fair_probabilities']['home']:.2%}",
        f"{report['fair_probabilities']['away']:.2%}"
    )
    
    table.add_row(
        "Model Probability",
        f"{report['model_probabilities']['home']:.2%}",
        f"{report['model_probabilities']['away']:.2%}"
    )
    
    home_edge = report['edge_analysis']['edge_pct']['home']
    away_edge = report['edge_analysis']['edge_pct']['away']
    
    table.add_row(
        "Edge",
        f"[green]{home_edge:+.2f}%[/green]" if home_edge > 0 else f"[red]{home_edge:+.2f}%[/red]",
        f"[green]{away_edge:+.2f}%[/green]" if away_edge > 0 else f"[red]{away_edge:+.2f}%[/red]"
    )
    
    console.print(table)
    
    # Final recommendation
    console.print()
    style = "bold green" if "RECOMMENDED" in report['recommendation'] else "bold yellow"
    console.print(Panel(
        report['recommendation'],
        title="💰 FINAL RECOMMENDATION",
        style=style
    ))
    
    console.print("\n[dim]Note: Each agent used Phi-3-mini LLM to reason about its specialized task![/dim]\n")


if __name__ == "__main__":
    main()
