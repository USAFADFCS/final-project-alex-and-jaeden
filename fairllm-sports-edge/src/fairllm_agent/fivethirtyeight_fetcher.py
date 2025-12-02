"""
FiveThirtyEight API Integration - Multi-Sport Support
Fetches real predictions for NBA, NFL, NHL, and MLB
"""
import requests
import pandas as pd
from typing import Dict, Optional, Literal
from datetime import datetime

SportType = Literal['NBA', 'NFL', 'NHL', 'MLB']

class FiveThirtyEightFetcher:
    """Fetches predictions from FiveThirtyEight for multiple sports"""
    
    # FiveThirtyEight's public API endpoints
    URLS = {
        'NBA': "https://projects.fivethirtyeight.com/nba-api/nba_elo_latest.csv",
        'NFL': "https://projects.fivethirtyeight.com/nfl-api/nfl_elo_latest.csv",
        'MLB': "https://projects.fivethirtyeight.com/mlb-api/mlb_elo_latest.csv",
        # NHL sometimes uses a different format
        'NHL': "https://projects.fivethirtyeight.com/nhl-api/nhl_elo_latest.csv"
    }
    
    def __init__(self, sport: SportType = 'NBA'):
        self.sport = sport.upper()
        self.data = None
        self.last_updated = None
    
    def fetch_latest_data(self) -> pd.DataFrame:
        """Fetch latest predictions for the selected sport"""
        try:
            print(f"📡 Fetching latest {self.sport} data from FiveThirtyEight...")
            
            if self.sport not in self.URLS:
                raise ValueError(f"Sport {self.sport} not supported. Choose from: {list(self.URLS.keys())}")
            
            url = self.URLS[self.sport]
            self.data = pd.read_csv(url, on_bad_lines='skip')
            self.last_updated = datetime.now()
            
            print(f"✅ Fetched {len(self.data)} {self.sport} games")
            return self.data
            
        except Exception as e:
            print(f"❌ Error fetching {self.sport} data: {e}")
            print(f"\n[yellow]Using demo {self.sport} data instead[/yellow]")
            
            # Create sample data as fallback
            self.data = self._create_demo_data()
            return self.data
    
    def _create_demo_data(self) -> pd.DataFrame:
        """Create demo data based on sport"""
        if self.sport == 'NBA':
            return pd.DataFrame({
                'date': ['2024-12-02', '2024-12-02', '2024-12-03'],
                'team1': ['Los Angeles Lakers', 'Golden State Warriors', 'Boston Celtics'],
                'team2': ['Denver Nuggets', 'Phoenix Suns', 'Miami Heat'],
                'elo1_pre': [1650, 1680, 1720],
                'elo2_pre': [1670, 1640, 1600],
                'elo_prob1': [0.47, 0.55, 0.63]
            })
        elif self.sport == 'NFL':
            return pd.DataFrame({
                'date': ['2024-12-08', '2024-12-08', '2024-12-09'],
                'team1': ['Kansas City Chiefs', 'San Francisco 49ers', 'Buffalo Bills'],
                'team2': ['Los Angeles Chargers', 'Seattle Seahawks', 'Los Angeles Rams'],
                'elo1_pre': [1700, 1680, 1690],
                'elo2_pre': [1620, 1640, 1630],
                'elo_prob1': [0.65, 0.58, 0.62]
            })
        elif self.sport == 'NHL':
            return pd.DataFrame({
                'date': ['2024-12-02', '2024-12-02', '2024-12-03'],
                'team1': ['Colorado Avalanche', 'Toronto Maple Leafs', 'Boston Bruins'],
                'team2': ['Vegas Golden Knights', 'Tampa Bay Lightning', 'Florida Panthers'],
                'elo1_pre': [1620, 1610, 1640],
                'elo2_pre': [1630, 1590, 1620],
                'elo_prob1': [0.48, 0.54, 0.52]
            })
        elif self.sport == 'MLB':
            return pd.DataFrame({
                'date': ['2024-07-15', '2024-07-15', '2024-07-16'],
                'team1': ['Los Angeles Dodgers', 'New York Yankees', 'Atlanta Braves'],
                'team2': ['San Diego Padres', 'Boston Red Sox', 'Philadelphia Phillies'],
                'elo1_pre': [1680, 1670, 1660],
                'elo2_pre': [1640, 1630, 1650],
                'elo_prob1': [0.56, 0.57, 0.52]
            })
        else:
            return pd.DataFrame()
    
    def get_game_prediction(self, team1: str, team2: str) -> Optional[Dict]:
        """Get prediction for a specific matchup"""
        if self.data is None:
            self.fetch_latest_data()
        
        team1_upper = team1.upper()
        team2_upper = team2.upper()
        
        # Search for teams
        filtered = self.data[
            ((self.data['team1'].str.upper().str.contains(team1_upper, na=False)) | 
             (self.data['team2'].str.upper().str.contains(team1_upper, na=False))) &
            ((self.data['team1'].str.upper().str.contains(team2_upper, na=False)) | 
             (self.data['team2'].str.upper().str.contains(team2_upper, na=False)))
        ]
        
        if len(filtered) > 0:
            game = filtered.iloc[0]
            
            # Determine home/away
            if team1_upper in str(game['team1']).upper():
                home_team = game['team1']
                away_team = game['team2']
                home_prob = game.get('elo_prob1', game.get('qbelo_prob1', game.get('raptor_prob1', 0.5)))
            else:
                home_team = game['team2']
                away_team = game['team1']
                home_prob = 1 - game.get('elo_prob1', game.get('qbelo_prob1', game.get('raptor_prob1', 0.5)))
            
            return {
                'home_team': str(home_team),
                'away_team': str(away_team),
                'home_prob': float(home_prob),
                'away_prob': float(1 - home_prob),
                'source': f'FiveThirtyEight {self.sport}',
                'sport': self.sport,
                'date': str(game.get('date', 'Unknown'))
            }
        
        return None
    
    def list_upcoming_games(self, limit: int = 10) -> pd.DataFrame:
        """List upcoming games"""
        if self.data is None:
            self.fetch_latest_data()
        
        cols_to_show = ['date', 'team1', 'team2']
        
        # Find probability column (varies by sport)
        prob_col = None
        for col in ['elo_prob1', 'qbelo_prob1', 'raptor_prob1']:
            if col in self.data.columns:
                prob_col = col
                break
        
        if prob_col:
            cols_to_show.append(prob_col)
        
        upcoming = self.data[cols_to_show].head(limit)
        
        rename_map = {'team1': 'Home', 'team2': 'Away'}
        if prob_col:
            rename_map[prob_col] = 'Home Win %'
            
        return upcoming.rename(columns=rename_map)
    
    def list_available_teams(self) -> list:
        """Get list of all teams in dataset"""
        if self.data is None:
            self.fetch_latest_data()
        
        teams = set(self.data['team1'].tolist() + self.data['team2'].tolist())
        return sorted(teams)


def convert_to_forecast_format(prediction: Dict) -> Dict:
    """Convert FiveThirtyEight prediction to forecast format"""
    return {
        "event_id": f"{prediction['date']}-{prediction['sport']}-{prediction['home_team']}-{prediction['away_team']}",
        "p_model": {
            "home": prediction['home_prob'],
            "away": prediction['away_prob']
        }
    }


# Test script
if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    
    console.print("\n[bold cyan]Testing FiveThirtyEight Multi-Sport Fetcher[/bold cyan]\n")
    
    for sport in ['NBA', 'NFL', 'NHL']:
        console.print(f"\n[yellow]Testing {sport}...[/yellow]")
        fetcher = FiveThirtyEightFetcher(sport)
        data = fetcher.fetch_latest_data()
        console.print(f"Available columns: {list(data.columns)[:5]}...")
        console.print(f"\nUpcoming {sport} games:")
        console.print(fetcher.list_upcoming_games(3))
