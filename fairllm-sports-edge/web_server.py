#!/usr/bin/env python3
"""
Flask Web Server for Sports Edge Chatbot
Run in browser at http://localhost:5000
"""

import sys
sys.path.insert(0, 'src')

from flask import Flask, render_template, request, jsonify
from fairllm_agent.agentic_workflow_llm import LLMSportsEdgeFlow
import re
import traceback

app = Flask(__name__)

# Initialize workflow
print("Loading AI agents...")
workflow = LLMSportsEdgeFlow()
print(f"✓ Loaded {len(workflow.agents)} AI agents")


@app.route('/')
def index():
    """Serve the main chat page"""
    return render_template('chat.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Process betting analysis request"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Parse the message
        parsed = parse_message(message)
        
        if not parsed:
            return jsonify({
                'error': 'Could not parse input. Use format: "Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%"'
            }), 400
        
        # Build odds and forecast data
        odds_data = {
            "event_id": f"web-{parsed['home']}-{parsed['away']}",
            "sport": "basketball",
            "league": "NBA",
            "home_team": parsed['home'],
            "away_team": parsed['away'],
            "sportsbook": "User Input",
            "moneyline": {
                "home": parsed['home_odds'],
                "away": parsed['away_odds']
            }
        }
        
        forecast_data = {
            "event_id": f"web-{parsed['home']}-{parsed['away']}",
            "p_model": {
                "home": parsed['home_prob'],
                "away": parsed['away_prob']
            }
        }
        
        # Run analysis
        report = workflow.run(odds_data, forecast_data)
        
        # Format response
        response = {
            'success': True,
            'teams': {
                'home': parsed['home'],
                'away': parsed['away']
            },
            'fair_odds': {
                'home': report['fair_probabilities']['home'],
                'away': report['fair_probabilities']['away']
            },
            'prediction': {
                'home': report['model_probabilities']['home'],
                'away': report['model_probabilities']['away']
            },
            'edge': {
                'home': report['edge_analysis']['edge_pct']['home'],
                'away': report['edge_analysis']['edge_pct']['away']
            },
            'recommendation': report['recommendation'],
            'insights': report.get('llm_insights', {})
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def parse_message(message):
    """Parse user message to extract game info"""
    try:
        message_lower = message.lower()
        
        # Extract teams
        if " vs " in message_lower or " v " in message_lower:
            parts = message_lower.replace(" v ", " vs ").split(" vs ")
            home = parts[0].strip().title()
            away = parts[1].split(",")[0].strip().title()
        else:
            words = message.split()
            home = words[0].title() if len(words) > 0 else "Home"
            away = words[1].title() if len(words) > 1 else "Away"
        
        # Extract odds
        odds_pattern = r"[-+]\d+"
        odds = re.findall(odds_pattern, message)
        
        if len(odds) >= 2:
            home_odds = int(odds[0])
            away_odds = int(odds[1])
        else:
            home_odds = -150
            away_odds = +130
        
        # Extract probability
        prob_pattern = r"(\d+)%?"
        probs = re.findall(prob_pattern, message)
        
        if probs:
            home_prob = float(probs[-1]) / 100
            home_prob = max(0.01, min(0.99, home_prob))
        else:
            home_prob = 0.55
        
        away_prob = 1.0 - home_prob
        
        return {
            "home": home,
            "away": away,
            "home_odds": home_odds,
            "away_odds": away_odds,
            "home_prob": home_prob,
            "away_prob": away_prob
        }
        
    except Exception:
        return None


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Sports Edge Chat - Web Version")
    print("="*60)
    print("\nOpen your browser and go to:")
    print("👉 http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
