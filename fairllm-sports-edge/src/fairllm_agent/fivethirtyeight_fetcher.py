"""
FiveThirtyEight API Integration
Fetches real NBA predictions from FiveThirtyEight's public data
"""
import requests
import pandas as pd
from typing import Dict, Optional
from datetime import datetime

class FiveThirtyEightFetcher:
    """Fetches NBA predictions from FiveThirtyEight"""
    
    NBA_ELO_URL = "https://projects.fivethirtyeight.com/nba-api/nba_elo_latest.csv"
    
    def __init__(self):
        self.data = None
        self.last_updated = None
    
    def fetch_latest_data(self) -> pd.DataFrame:
        """Fetch latest NBA predictions from FiveThirtyEight"""
        try:
            print("📡 Fetching latest data from FiveThirtyEight...")
            response = requests.get(self.NBA_ELO_URL, timeout=10)
            response.raise_for_status()
            
            from io import StringIO
            self.data = pd.read_csv(StringIO(response.text))
            self.last_updated = datetime.now()
            
            print(f"✅ Fetched {len(self.data)} games")
            return self.data
            
        except requests.RequestException as e:
            print(f"❌ Error: {e}")
            raise
    
    def get_game_prediction(self, team1: str, team2: str) -> Optional[Dict]:
        """Get prediction for a specific matchup"""
        if self.data is None:
            self.fetch_latest_data()
        
        team1_upper = team1.upper()
        team2_upper = team2.upper()
        
        filtered = self.data[
            (self.data['team1'].str.upper().str.contains(team1_upper) | 
             self.data['team1'].str.upper().str.contains(team2_upper)) &
            (self.data['team2'].str.upper().str.contains(team1_upper) | 
             self.data['team2'].str.upper().str.contains(team2_upper))
        ]
        
        if len(filtered) > 0:
            game = filtered.iloc[0]
            
            if team1_upper in game['team1'].upper():
                home_team = game['team1']
                away_team = game['team2']
                home_prob = game.get('team1_win_prob', game.get('elo_prob1', 0.5))
            else:
                home_team = game['team2']
                away_team = game['team1']
                home_prob = 1 - game.get('team1_win_prob', game.get('elo_prob1', 0.5))
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_prob': float(home_prob),
                'away_prob': float(1 - home_prob),
                'source': 'FiveThirtyEight',
                'date': game.get('date', 'Unknown')
            }
        
        return None
    
    def list_upcoming_games(self, limit: int = 10) -> pd.DataFrame:
        """List upcoming NBA games"""
        if self.data is None:
            self.fetch_latest_data()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        if 'date' in self.data.columns:
            upcoming = self.data[self.data['date'] >= today].head(limit)
        else:
            upcoming = self.data.head(limit)
        
        return upcoming[['date', 'team1', 'team2', 'team1_win_prob']].rename(columns={
            'team1': 'Home',
            'team2': 'Away',
            'team1_win_prob': 'Win%'
        })


def convert_to_forecast_format(prediction: Dict) -> Dict:
    """Convert FiveThirtyEight prediction to forecast format"""
    return {
        "event_id": f"{prediction['date']}-{prediction['home_team']}-{prediction['away_team']}",
        "p_model": {
            "home": prediction['home_prob'],
            "away": prediction['away_prob']
        }
    }
