"""
FiveThirtyEight API Integration - Multi-Sport Support
"""
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
        self.columns_info = {}
    
    def fetch_latest_data(self) -> pd.DataFrame:
        """Fetch latest predictions"""
        try:
            print(f"📡 Fetching {self.sport} data from FiveThirtyEight...")
            
            url = self.URLS[self.sport]
            
            # Try with SSL workaround
            try:
                self.data = pd.read_csv(url, on_bad_lines='skip')
            except:
                import urllib.request
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(url, context=context) as response:
                    self.data = pd.read_csv(response, on_bad_lines='skip')
            
            # Detect column structure
            self._detect_columns()
            
            # Filter for current season
            if self.columns_info['date']:
                date_col = self.columns_info['date']
                self.data[date_col] = pd.to_datetime(self.data[date_col], errors='coerce')
                today = pd.Timestamp.now()
                self.data = self.data[
                    (self.data[date_col] >= today - timedelta(days=30)) & 
                    (self.data[date_col] <= today + timedelta(days=60))
                ]
            
            self.last_updated = datetime.now()
            print(f"✅ Fetched {len(self.data)} games")
            return self.data
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            print(f"[yellow]Using demo data[/yellow]")
            self.data = self._create_demo_data()
            self._detect_columns()
            return self.data
    
    def _detect_columns(self):
        """Automatically detect column names"""
        cols = list(self.data.columns)
        print(f"[dim]Available columns: {', '.join(cols[:8])}{'...' if len(cols) > 8 else ''}[/dim]")
        
        # Find date column
        date_col = None
        for col in cols:
            if 'date' in col.lower():
                date_col = col
                break
        
        # Find team columns - look for patterns
        team1_col = None
        team2_col = None
        
        # Common patterns
        if 'team1' in cols and 'team2' in cols:
            team1_col, team2_col = 'team1', 'team2'
        elif 'home' in cols and 'away' in cols:
            team1_col, team2_col = 'home', 'away'
        else:
            # Look for any column with 'team' in it
            team_cols = [c for c in cols if 'team' in c.lower()]
            if len(team_cols) >= 2:
                team1_col, team2_col = team_cols[0], team_cols[1]
        
        # Find probability column
        prob_col = None
        for pattern in ['prob', 'win']:
            matching = [c for c in cols if pattern in c.lower()]
            if matching:
                # Prefer first team's probability
                prob_col = matching[0]
                break
        
        self.columns_info = {
            'date': date_col,
            'team1': team1_col,
            'team2': team2_col,
            'prob': prob_col
        }
        
        print(f"[dim]Detected: date={date_col}, team1={team1_col}, team2={team2_col}, prob={prob_col}[/dim]")
    
    def _create_demo_data(self) -> pd.DataFrame:
        """Create demo data"""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        date_str = lambda d: d.strftime('%Y-%m-%d')
        
        if self.sport == 'NBA':
            return pd.DataFrame({
                'date': [date_str(today), date_str(today), date_str(tomorrow)],
                'team1': ['Los Angeles Lakers', 'Golden State Warriors', 'Boston Celtics'],
                'team2': ['Denver Nuggets', 'Phoenix Suns', 'Miami Heat'],
                'elo_prob1': [0.47, 0.55, 0.63]
            })
        elif self.sport == 'NFL':
            days_until_sunday = (6 - today.weekday()) % 7 or 7
            next_sunday = today + timedelta(days=days_until_sunday)
            return pd.DataFrame({
                'date': [date_str(next_sunday), date_str(next_sunday), date_str(next_sunday + timedelta(1))],
                'team1': ['Kansas City Chiefs', 'San Francisco 49ers', 'Buffalo Bills'],
                'team2': ['Los Angeles Chargers', 'Seattle Seahawks', 'Los Angeles Rams'],
                'elo_prob1': [0.65, 0.58, 0.62]
            })
        elif self.sport == 'NHL':
            return pd.DataFrame({
                'date': [date_str(today), date_str(today), date_str(tomorrow)],
                'team1': ['Colorado Avalanche', 'Toronto Maple Leafs', 'Boston Bruins'],
                'team2': ['Vegas Golden Knights', 'Tampa Bay Lightning', 'Florida Panthers'],
                'elo_prob1': [0.48, 0.54, 0.52]
            })
        else:
            return pd.DataFrame({
                'date': [date_str(today), date_str(today), date_str(tomorrow)],
                'team1': ['Los Angeles Dodgers', 'New York Yankees', 'Atlanta Braves'],
                'team2': ['San Diego Padres', 'Boston Red Sox', 'Philadelphia Phillies'],
                'elo_prob1': [0.56, 0.57, 0.52]
            })
    
    def get_game_prediction(self, team1: str, team2: str) -> Optional[Dict]:
        """Get prediction for matchup"""
        if self.data is None or not self.columns_info['team1']:
            return None
        
        team1_col = self.columns_info['team1']
        team2_col = self.columns_info['team2']
        prob_col = self.columns_info['prob']
        
        team1_upper = team1.upper()
        team2_upper = team2.upper()
        
        # Search
        filtered = self.data[
            ((self.data[team1_col].str.upper().str.contains(team1_upper, na=False)) | 
             (self.data[team2_col].str.upper().str.contains(team1_upper, na=False))) &
            ((self.data[team1_col].str.upper().str.contains(team2_upper, na=False)) | 
             (self.data[team2_col].str.upper().str.contains(team2_upper, na=False)))
        ]
        
        if len(filtered) > 0:
            game = filtered.iloc[0]
            
            if team1_upper in str(game[team1_col]).upper():
                home_team = game[team1_col]
                away_team = game[team2_col]
                home_prob = float(game[prob_col]) if prob_col and prob_col in game else 0.5
            else:
                home_team = game[team2_col]
                away_team = game[team1_col]
                home_prob = 1 - float(game[prob_col]) if prob_col and prob_col in game else 0.5
            
            date_col = self.columns_info['date']
            game_date = game[date_col] if date_col else 'Unknown'
            if isinstance(game_date, pd.Timestamp):
                game_date = game_date.strftime('%Y-%m-%d')
            
            return {
                'home_team': str(home_team),
                'away_team': str(away_team),
                'home_prob': home_prob,
                'away_prob': 1 - home_prob,
                'source': f'FiveThirtyEight {self.sport}',
                'sport': self.sport,
                'date': str(game_date)
            }
        
        return None
    
    def list_upcoming_games(self, limit: int = 5) -> pd.DataFrame:
        """List upcoming games"""
        if self.data is None:
            self.fetch_latest_data()
        
        team1_col = self.columns_info['team1']
        team2_col = self.columns_info['team2']
        date_col = self.columns_info['date']
        prob_col = self.columns_info['prob']
        
        if not team1_col or not team2_col:
            # Return demo data if columns not found
            print("[yellow]Using demo game list[/yellow]")
            return pd.DataFrame({
                'Date': ['Today', 'Today', 'Tomorrow'],
                'Home': ['Lakers', 'Warriors', 'Celtics'],
                'Away': ['Nuggets', 'Suns', 'Heat'],
                'Win %': ['47%', '55%', '63%']
            })
        
        # Sort by date
        df = self.data.sort_values(date_col) if date_col else self.data
        
        # Select columns
        cols = []
        rename_map = {}
        
        if date_col:
            cols.append(date_col)
            rename_map[date_col] = 'Date'
        
        cols.extend([team1_col, team2_col])
        rename_map[team1_col] = 'Home'
        rename_map[team2_col] = 'Away'
        
        if prob_col:
            cols.append(prob_col)
            rename_map[prob_col] = 'Win %'
        
        upcoming = df[cols].head(limit).copy()
        
        # Format date
        if date_col and pd.api.types.is_datetime64_any_dtype(upcoming[date_col]):
            upcoming[date_col] = upcoming[date_col].dt.strftime('%Y-%m-%d')
        
        return upcoming.rename(columns=rename_map)


def convert_to_forecast_format(prediction: Dict) -> Dict:
    """Convert to forecast format"""
    return {
        "event_id": f"{prediction['date']}-{prediction['sport']}",
        "p_model": {
            "home": prediction['home_prob'],
            "away": prediction['away_prob']
        }
    }
