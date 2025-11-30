#!/usr/bin/env python3
"""
Evaluation script for FairLLM Sports Edge Analysis
Measures accuracy, edge detection, and recommendation quality
"""
import json
import argparse
from typing import Dict, List, Any
from pathlib import Path
import numpy as np
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


class EdgeEvaluator:
    """Evaluates the performance of the edge calculation system"""
    
    def __init__(self):
        self.metrics = {
            'total_games': 0,
            'positive_edges_found': 0,
            'average_edge': 0.0,
            'max_edge': 0.0,
            'recommendations': {'BET': 0, 'PASS': 0},
            'edge_distribution': []
        }
    
    def evaluate_reports(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a list of analysis reports
        
        Args:
            reports: List of edge analysis reports
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.metrics['total_games'] = len(reports)
        
        all_edges = []
        
        for report in reports:
            # Extract edge data
            edge_pct = report['edge_analysis']['edge_pct']
            max_edge = max(edge_pct['home'], edge_pct['away'])
            all_edges.append(max_edge)
            
            # Count positive edges
            if report['edge_analysis']['has_positive_edge']:
                self.metrics['positive_edges_found'] += 1
            
            # Count recommendations
            if "RECOMMENDED BET" in report['recommendation']:
                self.metrics['recommendations']['BET'] += 1
            else:
                self.metrics['recommendations']['PASS'] += 1
        
        # Calculate statistics
        if all_edges:
            self.metrics['average_edge'] = np.mean(all_edges)
            self.metrics['max_edge'] = np.max(all_edges)
            self.metrics['min_edge'] = np.min(all_edges)
            self.metrics['std_edge'] = np.std(all_edges)
            self.metrics['edge_distribution'] = all_edges
        
        # Calculate hit rate
        if self.metrics['total_games'] > 0:
            self.metrics['hit_rate'] = (
                self.metrics['positive_edges_found'] / self.metrics['total_games']
            )
            self.metrics['bet_rate'] = (
                self.metrics['recommendations']['BET'] / self.metrics['total_games']
            )
        
        return self.metrics
    
    def evaluate_with_outcomes(self, reports: List[Dict[str, Any]], 
                               outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate system performance against actual game outcomes
        
        Args:
            reports: List of edge analysis reports
            outcomes: List of actual game outcomes
            
        Returns:
            Dictionary of evaluation metrics including accuracy
        """
        basic_metrics = self.evaluate_reports(reports)
        
        correct_predictions = 0
        bet_wins = 0
        bet_losses = 0
        
        for report, outcome in zip(reports, outcomes):
            event_id = report['event_id']
            predicted_winner = report['model_prediction']
            actual_winner = outcome.get('winner')
            
            if actual_winner:
                # Check prediction accuracy
                if predicted_winner == actual_winner:
                    correct_predictions += 1
                
                # Check bet performance
                if "RECOMMENDED BET" in report['recommendation']:
                    # Extract recommended side
                    rec_side = None
                    for opp in report['edge_analysis']['opportunities']:
                        if opp['recommendation'] == 'BET':
                            rec_side = opp['side']
                            break
                    
                    if rec_side == actual_winner:
                        bet_wins += 1
                    else:
                        bet_losses += 1
        
        # Add outcome-based metrics
        if self.metrics['total_games'] > 0:
            basic_metrics['prediction_accuracy'] = correct_predictions / self.metrics['total_games']
        
        total_bets = bet_wins + bet_losses
        if total_bets > 0:
            basic_metrics['bet_win_rate'] = bet_wins / total_bets
            basic_metrics['bet_wins'] = bet_wins
            basic_metrics['bet_losses'] = bet_losses
            basic_metrics['total_bets'] = total_bets
        
        return basic_metrics
    
    def display_metrics(self, metrics: Dict[str, Any]):
        """Display evaluation metrics in formatted table"""
        console.print("\n[bold cyan]Evaluation Metrics[/bold cyan]\n")
        
        # Basic metrics table
        basic_table = Table(title="Basic Statistics", show_header=True)
        basic_table.add_column("Metric", style="cyan")
        basic_table.add_column("Value", justify="right", style="yellow")
        
        basic_table.add_row("Total Games", str(metrics['total_games']))
        basic_table.add_row("Games with Positive Edge", 
                           f"{metrics['positive_edges_found']} ({metrics.get('hit_rate', 0):.1%})")
        basic_table.add_row("Average Edge", f"{metrics['average_edge']:.2f}%")
        basic_table.add_row("Max Edge", f"{metrics['max_edge']:.2f}%")
        basic_table.add_row("Min Edge", f"{metrics.get('min_edge', 0):.2f}%")
        basic_table.add_row("Std Dev Edge", f"{metrics.get('std_edge', 0):.2f}%")
        
        console.print(basic_table)
        
        # Recommendation table
        rec_table = Table(title="Recommendations", show_header=True)
        rec_table.add_column("Type", style="cyan")
        rec_table.add_column("Count", justify="right", style="yellow")
        rec_table.add_column("Percentage", justify="right", style="green")
        
        total = metrics['total_games']
        for rec_type, count in metrics['recommendations'].items():
            pct = (count / total * 100) if total > 0 else 0
            rec_table.add_row(rec_type, str(count), f"{pct:.1f}%")
        
        console.print(rec_table)
        
        # Outcome-based metrics if available
        if 'prediction_accuracy' in metrics:
            outcome_table = Table(title="Outcome-Based Performance", show_header=True)
            outcome_table.add_column("Metric", style="cyan")
            outcome_table.add_column("Value", justify="right", style="yellow")
            
            outcome_table.add_row("Prediction Accuracy", f"{metrics['prediction_accuracy']:.1%}")
            
            if 'bet_win_rate' in metrics:
                outcome_table.add_row("Bet Win Rate", f"{metrics['bet_win_rate']:.1%}")
                outcome_table.add_row("Bets Won", str(metrics['bet_wins']))
                outcome_table.add_row("Bets Lost", str(metrics['bet_losses']))
                outcome_table.add_row("Total Bets Placed", str(metrics['total_bets']))
            
            console.print(outcome_table)
        
        console.print()


def main():
    parser = argparse.ArgumentParser(description="Evaluate FairLLM Sports Edge Analysis")
    parser.add_argument("--reports", required=True, help="Path to analysis reports JSON")
    parser.add_argument("--outcomes", help="Path to actual outcomes JSON (optional)")
    parser.add_argument("--out", default="evaluation_results.json", 
                       help="Output path for evaluation metrics")
    
    args = parser.parse_args()
    
    # Load reports
    with open(args.reports, 'r') as f:
        reports = json.load(f)
    
    # Initialize evaluator
    evaluator = EdgeEvaluator()
    
    # Run evaluation
    if args.outcomes:
        console.print(f"[yellow]Evaluating with actual outcomes...[/yellow]\n")
        with open(args.outcomes, 'r') as f:
            outcomes = json.load(f)
        metrics = evaluator.evaluate_with_outcomes(reports, outcomes)
    else:
        console.print(f"[yellow]Evaluating reports (no outcomes provided)...[/yellow]\n")
        metrics = evaluator.evaluate_reports(reports)
    
    # Display metrics
    evaluator.display_metrics(metrics)
    
    # Save metrics
    output_path = Path(args.out)
    output_path.write_text(json.dumps(metrics, indent=2, default=str))
    console.print(f"[green]✓ Evaluation results saved to {args.out}[/green]\n")


if __name__ == "__main__":
    main()