#!/usr/bin/env python3
"""Demo using real FiveThirtyEight predictions"""
import sys
sys.path.insert(0, 'src')

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from fairllm_agent.agentic_workflow import SportsEdgeFlow
from fairllm_agent.fivethirtyeight_fetcher import FiveThirtyEightFetcher, convert_to_forecast_format

console = Console()

def main():
    console.print(Panel.fit(
        "[bold magenta]FiveThirtyEight Integration Demo[/bold magenta]\n"
        "Using REAL NBA predictions!",
        border_style="magenta"
    ))
    
    console.print("\n[yellow]Initializing...[/yellow]")
    fetcher = FiveThirtyEightFetcher()
    workflow = SportsEdgeFlow()
    
    try:
        fetcher.fetch_latest_data()
        
        console.print("\n[bold cyan]Upcoming NBA Games:[/bold cyan]\n")
        upcoming = fetcher.list_upcoming_games(10)
        console.print(upcoming.to_string(index=False))
        
        console.print("\n[yellow]Enter team names to analyze (or 'quit')[/yellow]")
        
        while True:
            team1 = Prompt.ask("\nTeam 1 (e.g., Lakers)")
            if team1.lower() == 'quit':
                break
                
            team2 = Prompt.ask("Team 2")
            if team2.lower() == 'quit':
                break
            
            console.print(f"\n[cyan]Looking up {team1} vs {team2}...[/cyan]")
            prediction = fetcher.get_game_prediction(team1, team2)
            
            if not prediction:
                console.print(f"[red]❌ Game not found[/red]")
                continue
            
            console.print(f"[green]✅ Found: {prediction['home_team']} vs {prediction['away_team']}[/green]")
            console.print(f"   {prediction['home_team']}: {prediction['home_prob']:.1%}")
            console.print(f"   {prediction['away_team']}: {prediction['away_prob']:.1%}")
            
            console.print("\n[yellow]Enter current odds:[/yellow]")
            home_odds = int(Prompt.ask(f"{prediction['home_team']} odds"))
            away_odds = int(Prompt.ask(f"{prediction['away_team']} odds"))
            
            odds_data = {
                "event_id": f"{prediction['date']}-NBA",
                "sport": "basketball",
                "league": "NBA",
                "home_team": prediction['home_team'],
                "away_team": prediction['away_team'],
                "sportsbook": "User Input",
                "moneyline": {"home": home_odds, "away": away_odds}
            }
            
            forecast_data = convert_to_forecast_format(prediction)
            
            console.print("\n[yellow]Analyzing...[/yellow]")
            report = workflow.run(odds_data, forecast_data)
            
            console.print("\n" + "="*70)
            console.print("[bold]RESULTS (FiveThirtyEight predictions)[/bold]")
            console.print("="*70 + "\n")
            
            console.print(f"[cyan]Fair Odds:[/cyan]")
            console.print(f"  {report['matchup']['home']}: {report['fair_probabilities']['home']:.2%}")
            console.print(f"  {report['matchup']['away']}: {report['fair_probabilities']['away']:.2%}\n")
            
            console.print(f"[cyan]Edge:[/cyan]")
            for side in ['home', 'away']:
                edge = report['edge_analysis']['edge_pct'][side]
                color = "green" if edge > 0 else "red"
                console.print(f"  {report['matchup'][side]}: [{color}]{edge:+.2f}%[/{color}]")
            
            console.print()
            style = "bold green" if "RECOMMENDED" in report['recommendation'] else "bold yellow"
            console.print(Panel(report['recommendation'], style=style))
            
            if not Prompt.ask("\nAnother game?", choices=["y", "n"], default="y") == "y":
                break
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
    
    console.print("\n[cyan]Done![/cyan]\n")

if __name__ == "__main__":
    main()
