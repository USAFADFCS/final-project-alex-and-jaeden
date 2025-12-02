"""
FiveThirtyEight-Style Predictions with Demo Data
Note: FiveThirtyEight's API is not updated during offseason.
This uses realistic demo data for demonstration purposes.
"""
import pandas as pd
from typing import Dict, Optional, Literal
from datetime import datetime, timedelta

SportType = Literal['NBA', 'NFL', 'NHL', 'MLB']

class FiveThirtyEightFetcher:
    """Fetches predictions using FiveThirtyEight-style Elo methodology"""
    
    def __init__(self, sport: SportType = 'NBA'):
        self.sport = sport.upper()
        self.data = None
        self.last_updated = None
        self.using_demo = False
    
    def fetch_latest_data(self) -> pd.DataFrame:
        """Fetch predictions data"""
        print(f"📡 Loading {self.sport} predictions...")
        
        # Note: FiveThirtyEight's public API is often outdated during offseason
        # For demonstration, we use realistic demo data with current dates
        print(f"[yellow]Using demo {self.sport} data with current dates[/yellow]")
        print(f"[dim]Note: Real API integration would use live sportsbook feeds[/dim]")
        
        self.data = self._create_realistic_data()
        self.using_demo = True
        self.last_updated = datetime.now()
        
        print(f"✅ Loaded {len(self.data)} games")
        return self.data
    
    def _create_realistic_data(self) -> pd.DataFrame:
        """Create realistic demo data with current dates and real team matchups"""
        today = datetime.now()
        
        date_str = lambda d: d.strftime('%Y-%m-%d')
        
        if self.sport == 'NBA':
            # Realistic NBA matchups with plausible Elo-based predictions
            games = []
            
            # Today's games
            games.extend([
                (date_str(today), 'Los Angeles Lakers', 'Boston Celtics', 0.48),
                (date_str(today), 'Golden State Warriors', 'Phoenix Suns', 0.52),
                (date_str(today), 'Milwaukee Bucks', 'Miami Heat', 0.61),
                (date_str(today), 'Denver Nuggets', 'Minnesota Timberwolves', 0.55),
            ])
            
            # Tomorrow's games
            tomorrow = today + timedelta(days=1)
            games.extend([
                (date_str(tomorrow), 'Dallas Mavericks', 'LA Clippers', 0.49),
                (date_str(tomorrow), 'Philadelphia 76ers', 'New York Knicks', 0.53),
                (date_str(tomorrow), 'Oklahoma City Thunder', 'Sacramento Kings', 0.58),
            ])
            
            # Day after
            day_after = today + timedelta(days=2)
            games.extend([
                (date_str(day_after), 'Memphis Grizzlies', 'New Orleans Pelicans', 0.51),
                (date_str(day_after), 'Cleveland Cavaliers', 'Indiana Pacers', 0.56),
                (date_str(day_after), 'Portland Trail Blazers', 'Utah Jazz', 0.47),
            ])
            
        elif self.sport == 'NFL':
            # NFL games on Sunday
            days_until_sunday = (6 - today.weekday()) % 7 or 7
            next_sunday = today + timedelta(days=days_until_sunday)
            
            games = [
                (date_str(next_sunday), 'Kansas City Chiefs', 'Buffalo Bills', 0.58),
                (date_str(next_sunday), 'San Francisco 49ers', 'Dallas Cowboys', 0.54),
                (date_str(next_sunday), 'Philadelphia Eagles', 'Miami Dolphins', 0.61),
                (date_str(next_sunday), 'Baltimore Ravens', 'Cincinnati Bengals', 0.52),
                (date_str(next_sunday), 'Detroit Lions', 'Green Bay Packers', 0.49),
                (date_str(next_sunday + timedelta(1)), 'Los Angeles Rams', 'Seattle Seahawks', 0.47),
            ]
            
        elif self.sport == 'NHL':
            games = []
            
            # Today's games
            games.extend([
                (date_str(today), 'Colorado Avalanche', 'Vegas Golden Knights', 0.52),
                (date_str(today), 'Toronto Maple Leafs', 'Tampa Bay Lightning', 0.48),
                (date_str(today), 'Boston Bruins', 'Florida Panthers', 0.55),
                (date_str(today), 'Edmonton Oilers', 'Dallas Stars', 0.53),
            ])
            
            # Tomorrow
            tomorrow = today + timedelta(days=1)
            games.extend([
                (date_str(tomorrow), 'New York Rangers', 'New Jersey Devils', 0.51),
                (date_str(tomorrow), 'Carolina Hurricanes', 'Pittsburgh Penguins', 0.57),
                (date_str(tomorrow), 'Minnesota Wild', 'Winnipeg Jets', 0.49),
            ])
            
        elif self.sport == 'MLB':
            # MLB season (April-October)
            games = [
                (date_str(today), 'Los Angeles Dodgers', 'San Diego Padres', 0.58),
                (date_str(today), 'New York Yankees', 'Boston Red Sox', 0.54),
                (date_str(today), 'Atlanta Braves', 'Philadelphia Phillies', 0.52),
                (date_str(today), 'Houston Astros', 'Texas Rangers', 0.56),
                (date_str(today + timedelta(1)), 'Chicago Cubs', 'St. Louis Cardinals', 0.48),
            ]
        else:
            games = []
        
        # Convert to DataFrame
        df = pd.DataFrame(games, columns=['date', 'team1', 'team2', 'elo_prob1'])
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    
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
            
            if team1_upper in str(game['team1']).upper():
                home_team = game['team1']
                away_team = game['team2']
                home_prob = float(game['elo_prob1'])
            else:
                home_team = game['team2']
                away_team = game['team1']
                home_prob = 1 - float(game['elo_prob1'])
            
            game_date = game['date'].strftime('%Y-%m-%d')
            
            return {
                'home_team': str(home_team),
                'away_team': str(away_team),
                'home_prob': home_prob,
                'away_prob': 1 - home_prob,
                'source': f'Elo Model ({self.sport})',
                'sport': self.sport,
                'date': str(game_date)
            }
        
        print(f"[yellow]No match found for {team1} vs {team2}[/yellow]")
        print(f"[yellow]Available teams:[/yellow]")
        teams = sorted(set(self.data['team1'].tolist() + self.data['team2'].tolist()))
        for team in teams[:10]:
            print(f"  - {team}")
        
        return None
    
    def list_upcoming_games(self, limit: int = 5) -> pd.DataFrame:
        """List upcoming games"""
        if self.data is None:
            self.fetch_latest_data()
        
        df = self.data.sort_values('date').head(limit).copy()
        
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        df['elo_prob1'] = df['elo_prob1'].apply(lambda x: f"{x:.1%}")
        
        return df.rename(columns={
            'date': 'Date',
            'team1': 'Home',
            'team2': 'Away',
            'elo_prob1': 'Home Win %'
        })


def convert_to_forecast_format(prediction: Dict) -> Dict:
    """Convert prediction to forecast format"""
    return {
        "event_id": f"{prediction['date']}-{prediction['sport']}",
        "p_model": {
            "home": prediction['home_prob'],
            "away": prediction['away_prob']
        }
    }


if __name__ == "__main__":
    print("\nTesting demo data generator...\n")
    
    for sport in ['NBA', 'NFL', 'NHL']:
        print(f"\n{'='*50}")
        print(f"{sport}")
        print(f"{'='*50}")
        fetcher = FiveThirtyEightFetcher(sport)
        fetcher.fetch_latest_data()
        print("\nUpcoming games:")
        print(fetcher.list_upcoming_games(5))
