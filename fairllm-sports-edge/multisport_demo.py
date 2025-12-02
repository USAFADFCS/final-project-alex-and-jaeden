#!/usr/bin/env python3
"""Multi-Sport Demo using FiveThirtyEight predictions"""
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
        "[bold magenta]Multi-Sport FiveThirtyEight Demo[/bold magenta]\n"
        "NBA • NFL • NHL • MLB",
        border_style="magenta"
    ))
    
    # Choose sport
    console.print("\n[cyan]Available sports:[/cyan]")
    console.print("  1. NBA (Basketball)")
    console.print("  2. NFL (Football)")
    console.print("  3. NHL (Hockey)")
    console.print("  4. MLB (Baseball)")
    
    sport_choice = Prompt.ask("\nChoose sport", choices=["1", "2", "3", "4"], default="1")
    
    sport_map = {"1": "NBA", "2": "NFL", "3": "NHL", "4": "MLB"}
    sport = sport_map[sport_choice]
    
    console.print(f"\n[green]Selected: {sport}[/green]")
    
    # Initialize
    fetcher = FiveThirtyEightFetcher(sport)
    workflow = SportsEdgeFlow()
    
    try:
        fetcher.fetch_latest_data()
        
        console.print(f"\n[bold cyan]Upcoming {sport} Games:[/bold cyan]\n")
        upcoming = fetcher.list_upcoming_games(10)
        console.print(upcoming.to_string(index=False))
        
        console.print("\n[yellow]Enter team names to analyze (or 'quit')[/yellow]")
        console.print("[dim]Tip: Use partial names like 'Lakers' or 'Chiefs'[/dim]")
        
        while True:
            team1 = Prompt.ask(f"\n{sport} Team 1")
            if team1.lower() == 'quit':
                break
                
            team2 = Prompt.ask(f"{sport} Team 2")
            if team2.lower() == 'quit':
                break
            
            console.print(f"\n[cyan]Looking up {team1} vs {team2}...[/cyan]")
            prediction = fetcher.get_game_prediction(team1, team2)
            
            if not prediction:
                console.print(f"[red]❌ Game not found[/red]")
                console.print(f"\n[yellow]Available teams:[/yellow]")
                for team in fetcher.list_available_teams()[:15]:
                    console.print(f"  - {team}")
                continue
            
            console.print(f"[green]✅ {prediction['home_team']} vs {prediction['away_team']}[/green]")
            console.print(f"   FiveThirtyEight prediction:")
            console.print(f"   {prediction['home_team']}: {prediction['home_prob']:.1%}")
            console.print(f"   {prediction['away_team']}: {prediction['away_prob']:.1%}")
            
            console.print("\n[yellow]Enter current sportsbook odds:[/yellow]")
            home_odds = int(Prompt.ask(f"{prediction['home_team']} odds (e.g., -140)"))
            away_odds = int(Prompt.ask(f"{prediction['away_team']} odds (e.g., +120)"))
            
            odds_data = {
                "event_id": f"{prediction['date']}-{sport}",
                "sport": sport.lower(),
                "league": sport,
                "home_team": prediction['home_team'],
                "away_team": prediction['away_team'],
                "sportsbook": "User Input",
                "moneyline": {"home": home_odds, "away": away_odds}
            }
            
            forecast_data = convert_to_forecast_format(prediction)
            
            console.print("\n[yellow]Running multi-agent analysis...[/yellow]")
            report = workflow.run(odds_data, forecast_data)
            
            console.print("\n" + "="*70)
            console.print(f"[bold]{sport} ANALYSIS (FiveThirtyEight Model)[/bold]")
            console.print("="*70 + "\n")
            
            console.print(f"[cyan]Fair Probabilities (vig removed):[/cyan]")
            console.print(f"  {report['matchup']['home']}: {report['fair_probabilities']['home']:.2%}")
            console.print(f"  {report['matchup']['away']}: {report['fair_probabilities']['away']:.2%}\n")
            
            console.print(f"[cyan]FiveThirtyEight Model:[/cyan]")
            console.print(f"  {report['matchup']['home']}: {report['model_probabilities']['home']:.2%}")
            console.print(f"  {report['matchup']['away']}: {report['model_probabilities']['away']:.2%}\n")
            
            console.print(f"[cyan]Betting Edge:[/cyan]")
            for side in ['home', 'away']:
                edge = report['edge_analysis']['edge_pct'][side]
                color = "green" if edge > 0 else "red"
                console.print(f"  {report['matchup'][side]}: [{color}]{edge:+.2f}%[/{color}]")
            
            console.print()
            style = "bold green" if "RECOMMENDED" in report['recommendation'] else "bold yellow"
            console.print(Panel(report['recommendation'], style=style))
            
            if not Prompt.ask("\nAnalyze another game?", choices=["y", "n"], default="y") == "y":
                break
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
    
    console.print("\n[cyan]Thanks for using Multi-Sport Analysis![/cyan]\n")

if __name__ == "__main__":
    main()
