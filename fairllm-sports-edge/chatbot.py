#!/usr/bin/env python3
"""
Interactive Chatbot: Sports Edge Analysis Assistant
Talk to the LLM-powered multi-agent system!
"""
import sys
sys.path.insert(0, 'src')

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown
from fairllm_agent.agentic_workflow_llm import LLMSportsEdgeFlow

console = Console()

def print_header():
    console.print(Panel.fit(
        "[bold cyan]🤖 Sports Edge Analysis AI Assistant[/bold cyan]\n"
        "Chat with me to analyze betting opportunities!",
        border_style="cyan"
    ))

def print_agent_thinking(agent_name: str):
    console.print(f"\n[dim]🤔 {agent_name} is thinking...[/dim]")

def chat_loop():
    console.print("\n[yellow]Initializing AI agents...[/yellow]")
    workflow = LLMSportsEdgeFlow()
    console.print(f"[green]✓ Ready! I have {len(workflow.agents)} specialized agents:[/green]")
    console.print(f"  • [cyan]OddsAnalyzer[/cyan] - Removes vig from odds")
    console.print(f"  • [cyan]ForecastEvaluator[/cyan] - Validates predictions")
    console.print(f"  • [cyan]EdgeCalculator[/cyan] - Finds betting edges")
    console.print(f"  • [cyan]ReportGenerator[/cyan] - Makes recommendations\n")
    
    console.print("[bold]How to use:[/bold]")
    console.print("  1. Tell me the game (e.g., 'Lakers vs Celtics')")
    console.print("  2. Give me the odds (e.g., 'Lakers -140, Celtics +120')")
    console.print("  3. Share your prediction (e.g., 'I think Lakers have 62% chance')")
    console.print("  4. I'll analyze and recommend!\n")
    
    while True:
        console.print("\n" + "="*70)
        console.print("[bold magenta]💬 New Analysis[/bold magenta]")
        console.print("="*70 + "\n")
        
        # Step 1: Get game info
        console.print("[bold cyan]Step 1: What game do you want to analyze?[/bold cyan]")
        game_input = Prompt.ask("Enter matchup (e.g., 'Lakers vs Celtics')")
        
        if game_input.lower() in ['quit', 'exit', 'bye']:
            console.print("\n[cyan]👋 Thanks for chatting! Good luck with your bets![/cyan]\n")
            break
        
        # Parse teams
        if ' vs ' in game_input.lower():
            teams = game_input.split(' vs ')
            home_team = teams[0].strip()
            away_team = teams[1].strip()
        elif ' v ' in game_input.lower():
            teams = game_input.split(' v ')
            home_team = teams[0].strip()
            away_team = teams[1].strip()
        else:
            console.print("[yellow]I'll assume first team is home. Use 'Team1 vs Team2' format next time.[/yellow]")
            teams = game_input.split()
            home_team = teams[0] if len(teams) > 0 else "Home"
            away_team = teams[1] if len(teams) > 1 else "Away"
        
        console.print(f"[green]✓ Got it: {home_team} (home) vs {away_team} (away)[/green]\n")
        
        # Step 2: Get odds
        console.print("[bold cyan]Step 2: What are the current odds?[/bold cyan]")
        console.print("[dim]Format: 'Lakers -140, Celtics +120' or just type the numbers[/dim]")
        odds_input = Prompt.ask(f"Odds for {home_team} and {away_team}")
        
        # Parse odds
        try:
            odds_parts = odds_input.replace(',', ' ').split()
            home_odds = None
            away_odds = None
            
            for part in odds_parts:
                if part.lstrip('-+').isdigit():
                    if home_odds is None:
                        home_odds = int(part)
                    else:
                        away_odds = int(part)
            
            if home_odds is None or away_odds is None:
                raise ValueError("Need two odds")
                
        except:
            console.print("[yellow]Couldn't parse odds. Using defaults (-150, +130)[/yellow]")
            home_odds = -150
            away_odds = +130
        
        console.print(f"[green]✓ {home_team}: {home_odds:+d}, {away_team}: {away_odds:+d}[/green]\n")
        
        # Step 3: Get prediction
        console.print("[bold cyan]Step 3: What's your prediction?[/bold cyan]")
        console.print(f"[dim]What % chance does {home_team} have to win? (e.g., '60' for 60%)[/dim]")
        
        try:
            pred_input = Prompt.ask(f"Your prediction for {home_team}")
            home_prob = float(pred_input.rstrip('%')) / 100
            
            if home_prob < 0 or home_prob > 1:
                raise ValueError()
                
        except:
            console.print("[yellow]Using 55% as default[/yellow]")
            home_prob = 0.55
        
        away_prob = 1.0 - home_prob
        console.print(f"[green]✓ Your prediction: {home_team} {home_prob:.0%}, {away_team} {away_prob:.0%}[/green]\n")
        
        # Prepare data
        odds_data = {
            "event_id": f"chat-{home_team}-{away_team}",
            "sport": "basketball",
            "league": "NBA",
            "home_team": home_team,
            "away_team": away_team,
            "sportsbook": "User Input",
            "moneyline": {"home": home_odds, "away": away_odds}
        }
        
        forecast_data = {
            "event_id": f"chat-{home_team}-{away_team}",
            "p_model": {"home": home_prob, "away": away_prob}
        }
        
        # Run analysis
        console.print("[bold yellow]🤖 Running AI analysis...[/bold yellow]\n")
        
        try:
            report = workflow.run(odds_data, forecast_data)
            
            # Display in chatbot style
            console.print("\n" + "="*70)
            console.print("[bold]🎯 AI ANALYSIS RESULTS[/bold]")
            console.print("="*70 + "\n")
            
            # Show each agent's reasoning
            if 'llm_insights' in report:
                insights = report['llm_insights']
                
                console.print("[bold cyan]💭 Agent Reasoning:[/bold cyan]\n")
                
                if insights.get('odds_analysis'):
                    console.print(f"[cyan]OddsAnalyzer says:[/cyan] {insights['odds_analysis']}\n")
                
                if insights.get('forecast_evaluation'):
                    console.print(f"[cyan]ForecastEvaluator says:[/cyan] {insights['forecast_evaluation']}\n")
                
                if insights.get('edge_insight'):
                    console.print(f"[cyan]EdgeCalculator says:[/cyan] {insights['edge_insight']}\n")
            
            # Show math
            console.print("[bold]📊 The Numbers:[/bold]")
            console.print(f"  Fair odds (vig removed): {home_team} {report['fair_probabilities']['home']:.1%}, {away_team} {report['fair_probabilities']['away']:.1%}")
            console.print(f"  Your prediction: {home_team} {report['model_probabilities']['home']:.1%}, {away_team} {report['model_probabilities']['away']:.1%}")
            
            home_edge = report['edge_analysis']['edge_pct']['home']
            away_edge = report['edge_analysis']['edge_pct']['away']
            
            if home_edge > 0:
                console.print(f"  [green]Edge found: {home_team} has {home_edge:+.2f}% edge![/green]")
            elif away_edge > 0:
                console.print(f"  [green]Edge found: {away_team} has {away_edge:+.2f}% edge![/green]")
            else:
                console.print(f"  [yellow]No significant edge found[/yellow]")
            
            # Final recommendation
            console.print()
            rec = report['recommendation']
            if "RECOMMENDED BET" in rec:
                console.print(Panel(
                    f"[bold green]{rec}[/bold green]",
                    title="💰 MY RECOMMENDATION",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[bold yellow]{rec}[/bold yellow]",
                    title="⚠️ MY RECOMMENDATION",
                    border_style="yellow"
                ))
            
            # Ask if they want details
            if Confirm.ask("\n[dim]Want to see detailed breakdown?[/dim]", default=False):
                console.print("\n[bold]Full Report:[/bold]")
                console.print(report)
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            import traceback
            traceback.print_exc()
        
        # Continue?
        console.print()
        if not Confirm.ask("[bold]Analyze another game?[/bold]", default=True):
            console.print("\n[cyan]👋 Thanks for using Sports Edge AI! Bet responsibly![/cyan]\n")
            break


def main():
    print_header()
    
    console.print("\n[bold]Welcome! I'm your AI sports betting analyst.[/bold]")
    console.print("I use 4 specialized agents to analyze betting opportunities.\n")
    
    console.print("[dim]Type 'quit' or 'exit' anytime to leave.[/dim]\n")
    
    try:
        chat_loop()
    except KeyboardInterrupt:
        console.print("\n\n[cyan]👋 Goodbye![/cyan]\n")


if __name__ == "__main__":
    main()
