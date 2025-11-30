#!/usr/bin/env python3
"""
Enhanced CLI for FairLLM Sports Edge Analysis
Demonstrates multi-agent workflow for betting edge calculation
"""
from __future__ import annotations
import json
import argparse
import pathlib
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from fairllm_agent.agentic_workflow import SportsEdgeFlow
from fairllm_agent.odds_fetcher import OddsFetcher

console = Console()


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load JSON data from file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def display_report(report: Dict[str, Any], verbose: bool = False):
    """Display analysis report in formatted output"""
    
    # Event header
    console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
    console.print(f"[bold]Event Analysis: {report['event_id']}[/bold]")
    console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")
    
    # Matchup info
    matchup = report['matchup']
    console.print(f"[yellow]Sport:[/yellow] {report['sport']} - {report['league']}")
    console.print(f"[yellow]Matchup:[/yellow] {matchup['home']} (Home) vs {matchup['away']} (Away)")
    console.print(f"[yellow]Sportsbook:[/yellow] {report['sportsbook']}\n")
    
    # Odds table
    odds_table = Table(title="Odds & Probabilities", show_header=True, header_style="bold magenta")
    odds_table.add_column("Side", style="cyan", width=12)
    odds_table.add_column("American Odds", justify="right")
    odds_table.add_column("Fair Prob", justify="right")
    odds_table.add_column("Model Prob", justify="right")
    odds_table.add_column("Edge", justify="right")
    
    for side in ["home", "away"]:
        odds = report['original_odds'][side]
        fair_p = report['fair_probabilities'][side]
        model_p = report['model_probabilities'][side]
        edge_pct = report['edge_analysis']['edge_pct'][side]
        
        edge_color = "green" if edge_pct > 0 else "red"
        odds_table.add_row(
            side.upper(),
            f"{odds:+d}",
            f"{fair_p:.2%}",
            f"{model_p:.2%}",
            f"[{edge_color}]{edge_pct:+.2f}%[/{edge_color}]"
        )
    
    console.print(odds_table)
    console.print()
    
    # Model prediction
    prediction = report['model_prediction']
    confidence = report['model_confidence']
    console.print(f"[yellow]Model Prediction:[/yellow] {prediction.upper()} ({confidence:.1%} confidence margin)")
    
    # Edge opportunities
    if report['edge_analysis']['opportunities']:
        console.print("\n[bold yellow]Opportunities:[/bold yellow]")
        for opp in report['edge_analysis']['opportunities']:
            if opp['recommendation'] == 'BET':
                console.print(
                    f"  [green]✓[/green] {opp['side'].upper()}: "
                    f"{opp['edge_pct']:.2f}% edge - {opp['confidence']} confidence"
                )
            else:
                console.print(
                    f"  [red]✗[/red] {opp['side'].upper()}: "
                    f"{opp['edge_pct']:.2f}% negative edge - AVOID"
                )
    
    # Final recommendation
    rec = report['recommendation']
    if "RECOMMENDED BET" in rec:
        console.print(Panel(rec, style="bold green", title="Recommendation"))
    else:
        console.print(Panel(rec, style="bold yellow", title="Recommendation"))
    
    # Verbose mode: show agent analyses
    if verbose:
        console.print("\n[bold]Agent Analyses:[/bold]")
        for agent_name, analysis in report['agent_analyses'].items():
            console.print(f"  [cyan]{agent_name.title()}:[/cyan] {analysis}")
    
    console.print()


def display_batch_summary(reports: List[Dict[str, Any]]):
    """Display summary of batch analysis"""
    console.print("\n[bold cyan]Batch Analysis Summary[/bold cyan]\n")
    
    total = len(reports)
    with_edge = sum(1 for r in reports if r['edge_analysis']['has_positive_edge'])
    
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("Event ID", style="cyan")
    summary_table.add_column("Matchup")
    summary_table.add_column("Best Edge", justify="right")
    summary_table.add_column("Recommendation", style="bold")
    
    for report in reports:
        event_id = report['event_id']
        matchup = f"{report['matchup']['home']} vs {report['matchup']['away']}"
        
        # Find best edge
        edges = report['edge_analysis']['edge_pct']
        best_edge = max(edges['home'], edges['away'])
        best_side = 'home' if edges['home'] > edges['away'] else 'away'
        
        # Get recommendation
        rec = "BET" if "RECOMMENDED BET" in report['recommendation'] else "PASS"
        rec_color = "green" if rec == "BET" else "yellow"
        
        summary_table.add_row(
            event_id,
            matchup,
            f"{best_edge:+.2f}% ({best_side})",
            f"[{rec_color}]{rec}[/{rec_color}]"
        )
    
    console.print(summary_table)
    console.print(f"\n[yellow]Total Games:[/yellow] {total}")
    console.print(f"[green]Games with Positive Edge:[/green] {with_edge} ({with_edge/total:.1%})")
    console.print()


def main():
    parser = argparse.ArgumentParser(
        description="FairLLM Sports Edge Analysis - Multi-Agent Betting Edge Calculator"
    )
    parser.add_argument(
        "--odds",
        default="data/samples/odds_demo.json",
        help="Path to odds JSON file"
    )
    parser.add_argument(
        "--forecast",
        default="data/samples/forecast_demo.json",
        help="Path to forecast JSON file"
    )
    parser.add_argument(
        "--out",
        default="edge_report.json",
        help="Output path for JSON report"
    )
    parser.add_argument(
        "--batch",
        help="Path to batch input file (list of {odds, forecast} pairs)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed agent analyses"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only output JSON, no console display"
    )
    
    args = parser.parse_args()
    
    # Initialize the multi-agent workflow
    if not args.quiet:
        console.print("\n[bold green]Initializing FairLLM Sports Edge Analysis[/bold green]")
        console.print("[cyan]Loading specialized agents:[/cyan]")
        console.print("  • OddsAnalyzer - Converting odds to fair probabilities")
        console.print("  • ForecastEvaluator - Validating model predictions")
        console.print("  • EdgeCalculator - Computing betting edges")
        console.print("  • ReportGenerator - Synthesizing final analysis")
    
    workflow = SportsEdgeFlow()
    
    if args.batch:
        # Batch processing mode
        if not args.quiet:
            console.print(f"\n[yellow]Running batch analysis from {args.batch}[/yellow]\n")
        
        with open(args.batch, 'r') as f:
            batch_data = json.load(f)
        
        games = [(item['odds'], item['forecast']) for item in batch_data]
        reports = workflow.run_batch(games)
        
        # Save batch results
        output_path = pathlib.Path(args.out)
        output_path.write_text(json.dumps(reports, indent=2))
        
        if not args.quiet:
            # Display individual reports
            for report in reports:
                display_report(report, args.verbose)
            
            # Display summary
            display_batch_summary(reports)
            console.print(f"[green]✓ Batch results saved to {args.out}[/green]\n")
    
    else:
        # Single game mode
        if not args.quiet:
            console.print(f"\n[yellow]Analyzing single game[/yellow]")
            console.print(f"  Odds: {args.odds}")
            console.print(f"  Forecast: {args.forecast}\n")
        
        # Load data
        odds_data = load_json_file(args.odds)
        forecast_data = load_json_file(args.forecast)
        
        # Run workflow
        report = workflow.run(odds_data, forecast_data)
        
        # Save results
        output_path = pathlib.Path(args.out)
        output_path.write_text(json.dumps(report, indent=2))
        
        if args.quiet:
            # Just print JSON
            print(json.dumps(report, indent=2))
        else:
            # Display formatted report
            display_report(report, args.verbose)
            console.print(f"[green]✓ Report saved to {args.out}[/green]\n")


if __name__ == "__main__":
    main()