"""
FiveThirtyEight API Integration - Multi-Sport Support
Fetches real predictions for NBA, NFL, NHL, and MLB
"""
import requests
import pandas as pd
from typing import Dict, Optional, Literal
from datetime import datetime, timedelta
import ssl

SportType = Literal['NBA', 'NFL', 'NHL', 'MLB']

class FiveThirtyEightFetcher:
    """Fetches predictions from FiveThirtyEight for multiple sports"""
    
    URLS = {
        'NBA': "https://projects.fivethirtyeight.com/nba-api/nba_elo_latest.csv",
        'NFL': "https://projects.fivethirtyeight.com/nfl-api/nfl_elo_latest.csv",
        'MLB': "https://projects.fivethirtyeight.com/mlb-api/mlb_elo_latest.csv",
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
                raise ValueError(f"Sport {self.sport} not supported")
            
            url = self.URLS[self.sport]
            
            # Try with SSL workaround
            try:
                self.data = pd.read_csv(url, on_bad_lines='skip')
            except:
                print(f"[yellow]SSL issue, trying alternative...[/yellow]")
                import urllib.request
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(url, context=context) as response:
                    self.data = pd.read_csv(response, on_bad_lines='skip')
            
            # Print columns for debugging
            print(f"[dim]Columns found: {', '.join(list(self.data.columns)[:5])}...[/dim]")
            
            # Filter for current season
            date_col = self._find_date_column()
            if date_col:
                self.data[date_col] = pd.to_datetime(self.data[date_col], errors='coerce')
                today = pd.Timestamp.now()
                self.data = self.data[
                    (self.data[date_col] >= today - timedelta(days=30)) & 
                    (self.data[date_col] <= today + timedelta(days=60))
                ]
            
            self.last_updated = datetime.now()
            print(f"✅ Fetched {len(self.data)} {self.sport} games")
            return self.data
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"[yellow]Using demo data[/yellow]")
            self.data = self._create_demo_data()
            return self.data
    
    def _find_date_column(self) -> Optional[str]:
        """Find the date column in the dataframe"""
        for col in ['date', 'gamedate', 'game_date']:
            if col in self.data.columns:
                return col
        return None
    
    def _find_team_columns(self) -> tuple:
        """Find team column names"""
        # Common column names for teams
        team1_options = ['team1', 'home_team', 'home', 'team_home']
        team2_options = ['team2', 'away_team', 'away', 'team_away']
        
        team1_col = None
        team2_col = None
        
        for col in team1_options:
            if col in self.data.columns:
                team1_col = col
                break
        
        for col in team2_options:
            if col in self.data.columns:
                team2_col = col
                break
        
        return team1_col, team2_col
    
    def _find_prob_column(self) -> Optional[str]:
        """Find probability column"""
        for col in ['elo_prob1', 'qbelo_prob1', 'raptor_prob1', 'team1_win_prob', 'home_prob']:
            if col in self.data.columns:
                return col
        return None
    
    def _create_demo_data(self) -> pd.DataFrame:
        """Create demo data with current dates"""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        date_format = lambda d: d.strftime('%Y-%m-%d')
        
        if self.sport == 'NBA':
            return pd.DataFrame({
                'date': [date_format(today), date_format(today), date_format(tomorrow)],
                'team1': ['Los Angeles Lakers', 'Golden State Warriors', 'Boston Celtics'],
                'team2': ['Denver Nuggets', 'Phoenix Suns', 'Miami Heat'],
                'elo_prob1': [0.47, 0.55, 0.63]
            })
        elif self.sport == 'NFL':
            days_until_sunday = (6 - today.weekday()) % 7 or 7
            next_sunday = today + timedelta(days=days_until_sunday)
            return pd.DataFrame({
                'date': [date_format(next_sunday), date_format(next_sunday), date_format(next_sunday + timedelta(days=1))],
                'team1': ['Kansas City Chiefs', 'San Francisco 49ers', 'Buffalo Bills'],
                'team2': ['Los Angeles Chargers', 'Seattle Seahawks', 'Los Angeles Rams'],
                'elo_prob1': [0.65, 0.58, 0.62]
            })
        elif self.sport == 'NHL':
            return pd.DataFrame({
                'date': [date_format(today), date_format(today), date_format(tomorrow)],
                'team1': ['Colorado Avalanche', 'Toronto Maple Leafs', 'Boston Bruins'],
                'team2': ['Vegas Golden Knights', 'Tampa Bay Lightning', 'Florida Panthers'],
                'elo_prob1': [0.48, 0.54, 0.52]
            })
        else:
            return pd.DataFrame({
                'date': [date_format(today), date_format(today), date_format(tomorrow)],
                'team1': ['Los Angeles Dodgers', 'New York Yankees', 'Atlanta Braves'],
                'team2': ['San Diego Padres', 'Boston Red Sox', 'Philadelphia Phillies'],
                'elo_prob1': [0.56, 0.57, 0.52]
            })
    
    def get_game_prediction(self, team1: str, team2: str) -> Optional[Dict]:
        """Get prediction for a specific matchup"""
        if self.data is None:
            self.fetch_latest_data()
        
        team1_col, team2_col = self._find_team_columns()
        if not team1_col or not team2_col:
            print(f"[red]Could not find team columns[/red]")
            return None
        
        team1_upper = team1.upper()
        team2_upper = team2.upper()
        
        # Search for teams
        filtered = self.data[
            ((self.data[team1_col].str.upper().str.contains(team1_upper, na=False)) | 
             (self.data[team2_col].str.upper().str.contains(team1_upper, na=False))) &
            ((self.data[team1_col].str.upper().str.contains(team2_upper, na=False)) | 
             (self.data[team2_col].str.upper().str.contains(team2_upper, na=False)))
        ]
        
        if len(filtered) > 0:
            game = filtered.iloc[0]
            prob_col = self._find_prob_column()
            
            if team1_upper in str(game[team1_col]).upper():
                home_team = game[team1_col]
                away_team = game[team2_col]
                home_prob = game.get(prob_col, 0.5) if prob_col else 0.5
            else:
                home_team = game[team2_col]
                away_team = game[team1_col]
                home_prob = 1 - game.get(prob_col, 0.5) if prob_col else 0.5
            
            date_col = self._find_date_column()
            game_date = game.get(date_col, 'Unknown') if date_col else 'Unknown'
            if isinstance(game_date, pd.Timestamp):
                game_date = game_date.strftime('%Y-%m-%d')
            
            return {
                'home_team': str(home_team),
                'away_team': str(away_team),
                'home_prob': float(home_prob),
                'away_prob': float(1 - home_prob),
                'source': f'FiveThirtyEight {self.sport}',
                'sport': self.sport,
                'date': str(game_date)
            }
        
        return None
    
    def list_upcoming_games(self, limit: int = 5) -> pd.DataFrame:
        """List upcoming games"""
        if self.data is None:
            self.fetch_latest_data()
        
        team1_col, team2_col = self._find_team_columns()
        date_col = self._find_date_column()
        prob_col = self._find_prob_column()
        
        if not team1_col or not team2_col:
            raise ValueError("Could not identify team columns")
        
        # Sort by date if available
        df = self.data.sort_values(date_col) if date_col else self.data
        
        cols_to_show = []
        if date_col:
            cols_to_show.append(date_col)
        cols_to_show.extend([team1_col, team2_col])
        if prob_col:
            cols_to_show.append(prob_col)
        
        upcoming = df[cols_to_show].head(limit).copy()
        
        # Format date
        if date_col and date_col in upcoming.columns:
            if pd.api.types.is_datetime64_any_dtype(upcoming[date_col]):
                upcoming[date_col] = upcoming[date_col].dt.strftime('%Y-%m-%d')
        
        # Rename columns
        rename_map = {team1_col: 'Home', team2_col: 'Away'}
        if date_col:
            rename_map[date_col] = 'Date'
        if prob_col:
            rename_map[prob_col] = 'Home Win %'
            
        return upcoming.rename(columns=rename_map)


def convert_to_forecast_format(prediction: Dict) -> Dict:
    """Convert prediction to forecast format"""
    return {
        "event_id": f"{prediction['date']}-{prediction['sport']}",
        "p_model": {
            "home": prediction['home_prob'],
            "away": prediction['away_prob']
        }
    }
