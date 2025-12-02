#!/usr/bin/env python3
"""
Interactive Sports Edge Analysis
"""
import sys
sys.path.insert(0, 'src')

from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.table import Table
from fairllm_agent.agentic_workflow import SportsEdgeFlow

console = Console()

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
            # Choose prediction source
            console.print("\n[bold cyan]Choose Prediction Source[/bold cyan]\n")
            console.print("1. Manual input")
            console.print("2. FiveThirtyEight")
            
            source_choice = Prompt.ask("Choice", choices=["1", "2"], default="2")
            use_fivethirtyeight = (source_choice == "2")
            
            # Get sport
            console.print("\n[bold cyan]Select Sport[/bold cyan]\n")
            console.print("1. NBA")
            console.print("2. NFL")
            console.print("3. NHL")
            console.print("4. MLB")
            
            sport_choice = Prompt.ask("Sport", choices=["1", "2", "3", "4"], default="1")
            sport_map = {
                "1": {"name": "NBA", "league": "NBA", "sport": "basketball"},
                "2": {"name": "NFL", "league": "NFL", "sport": "football"},
                "3": {"name": "NHL", "league": "NHL", "sport": "hockey"},
                "4": {"name": "MLB", "league": "MLB", "sport": "baseball"}
            }
            sport_info = sport_map[sport_choice]
            
            # Show upcoming games if FiveThirtyEight
            fetcher = None
            if use_fivethirtyeight:
                fetcher = show_upcoming_games(sport_info['name'])
            
            # Get teams
            console.print(f"\n[bold cyan]Enter {sport_info['name']} Teams[/bold cyan]\n")
            if use_fivethirtyeight:
                console.print("[dim]Tip: Use team names from above[/dim]")
            home_team = Prompt.ask("Home Team")
            away_team = Prompt.ask("Away Team")
            
            # Get odds (no sportsbook question)
            console.print("\n[bold cyan]Enter Odds[/bold cyan]\n")
            console.print("[yellow]American format (e.g., -150 or +130)[/yellow]")
            home_odds = IntPrompt.ask(f"{home_team} odds")
            away_odds = IntPrompt.ask(f"{away_team} odds")
            
            odds_data = {
                "event_id": f"{sport_info['name']}-{home_team}-{away_team}",
                "sport": sport_info['sport'],
                "league": sport_info['league'],
                "home_team": home_team,
                "away_team": away_team,
                "sportsbook": "Market Odds",
                "moneyline": {"home": home_odds, "away": away_odds}
            }
            
            # Get prediction
            if use_fivethirtyeight:
                forecast_data = get_fivethirtyeight_forecast(fetcher, sport_info['name'], home_team, away_team)
            else:
                forecast_data = get_manual_forecast(home_team, away_team)
            
            console.print("\n[yellow]Running analysis...[/yellow]")
            report = workflow.run(odds_data, forecast_data)
            
            if 'source' in forecast_data:
                report['source'] = forecast_data['source']
            
            display_report(report)
            
            console.print()
            if not Confirm.ask("Analyze another game?", default=True):
                break
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            if not Confirm.ask("\nTry again?", default=True):
                break
    
    console.print("\n[cyan]Thanks for using Sports Edge Analysis![/cyan]\n")

def show_upcoming_games(sport):
    """Show upcoming games"""
    try:
        from fairllm_agent.fivethirtyeight_fetcher import FiveThirtyEightFetcher
        
        console.print(f"\n[yellow]📡 Fetching {sport} schedule...[/yellow]")
        fetcher = FiveThirtyEightFetcher(sport)
        fetcher.fetch_latest_data()
        
        console.print(f"\n[bold cyan]Upcoming {sport} Games:[/bold cyan]\n")
        upcoming = fetcher.list_upcoming_games(5)
        
        table = Table(show_header=True, header_style="bold cyan")
        for col in upcoming.columns:
            table.add_column(col)
        
        for _, row in upcoming.iterrows():
            table.add_row(*[str(val) for val in row])
        
        console.print(table)
        return fetcher
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return None

def get_manual_forecast(home_team, away_team):
    """Get manual forecast"""
    console.print("\n[bold cyan]Enter Your Prediction[/bold cyan]\n")
    console.print("[yellow]Home team win probability (0.0 to 1.0)[/yellow]\n")
    
    home_prob = float(Prompt.ask(f"{home_team} probability"))
    away_prob = 1.0 - home_prob
    
    console.print(f"[dim]{away_team}: {away_prob:.2%}[/dim]")
    
    return {
        "event_id": f"{home_team}-{away_team}",
        "p_model": {"home": home_prob, "away": away_prob},
        "source": "Manual Input"
    }

def get_fivethirtyeight_forecast(fetcher, sport, home_team, away_team):
    """Get FiveThirtyEight forecast"""
    try:
        from fairllm_agent.fivethirtyeight_fetcher import FiveThirtyEightFetcher, convert_to_forecast_format
        
        if fetcher is None:
            console.print(f"\n[yellow]Fetching {sport} data...[/yellow]")
            fetcher = FiveThirtyEightFetcher(sport)
            fetcher.fetch_latest_data()
        
        console.print(f"\n[yellow]Looking up game...[/yellow]")
        prediction = fetcher.get_game_prediction(home_team, away_team)
        
        if prediction:
            console.print(f"[green]✅ {prediction['home_team']} vs {prediction['away_team']}[/green]")
            console.print(f"   Prediction: {prediction['home_prob']:.1%} / {prediction['away_prob']:.1%}")
            
            forecast = convert_to_forecast_format(prediction)
            forecast['source'] = f"FiveThirtyEight {sport}"
            return forecast
        else:
            console.print("[red]❌ Game not found[/red]")
            console.print("[yellow]Using manual input...[/yellow]")
            return get_manual_forecast(home_team, away_team)
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("[yellow]Using manual input...[/yellow]")
        return get_manual_forecast(home_team, away_team)

def display_report(report):
    """Display report"""
    console.print("\n" + "="*70)
    console.print("[bold]ANALYSIS RESULTS[/bold]")
    console.print("="*70 + "\n")
    
    console.print(f"[yellow]Matchup:[/yellow] {report['matchup']['home']} vs {report['matchup']['away']}")
    console.print(f"[yellow]League:[/yellow] {report['league']}")
    if 'source' in report:
        console.print(f"[yellow]Prediction:[/yellow] {report['source']}")
    console.print()
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Team")
    table.add_column("Odds", justify="right")
    table.add_column("Fair Prob", justify="right")
    table.add_column("Model Prob", justify="right")
    table.add_column("Edge", justify="right")
    
    for side in ['home', 'away']:
        edge = report['edge_analysis']['edge_pct'][side]
        color = "green" if edge > 0 else "red"
        
        table.add_row(
            report['matchup'][side],
            f"{report['original_odds'][side]:+d}",
            f"{report['fair_probabilities'][side]:.2%}",
            f"{report['model_probabilities'][side]:.2%}",
            f"[{color}]{edge:+.2f}%[/{color}]"
        )
    
    console.print(table)
    console.print()
    
    style = "bold green" if "RECOMMENDED" in report['recommendation'] else "bold yellow"
    console.print(Panel(report['recommendation'], style=style))

if __name__ == "__main__":
    main()
