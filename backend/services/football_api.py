# backend/services/football_api.py
import httpx
import asyncio
import json
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
import hashlib

class FootballAPIService:
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    LEAGUES = {
        "premier_league":    {"id": 39,  "name": "Premier League"},
        "la_liga":           {"id": 140, "name": "La Liga"},
        "champions_league":  {"id": 2,   "name": "Champions League"},
        "ligue_1":           {"id": 61,  "name": "Ligue 1"},
        "bundesliga":        {"id": 78,  "name": "Bundesliga"},
        "serie_a":           {"id": 135, "name": "Serie A"}
    }
    
    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_API_KEY", "")
        self.season = 2024
        self._cache: Dict[str, Any] = {}
        
        if not self.api_key:
            print("⚠️  WARNING: FOOTBALL_API_KEY not set!")
            print("   Get free key at: rapidapi.com/api-sports")
        
        self.headers = {
            "x-apisports-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
    
    def _cache_key(self, endpoint: str, params: dict) -> str:
        key_str = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def _request(
        self, 
        endpoint: str, 
        params: dict,
        cache_minutes: int = 60
    ) -> dict:
        """Request avec cache en mémoire"""
        cache_key = self._cache_key(endpoint, params)
        
        # Vérifie cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            age = (datetime.now() - cached_time).seconds / 60
            if age < cache_minutes:
                return cached_data
        
        # Si pas de clé API → retourne données démo
        if not self.api_key or self.api_key == "your_api_football_key_here":
            return self._get_demo_data(endpoint, params)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/{endpoint}",
                    headers=self.headers,
                    params=params
                )
                data = response.json()
                
                # Stocke dans cache
                self._cache[cache_key] = (data, datetime.now())
                return data
                
        except Exception as e:
            print(f"API Error [{endpoint}]: {e}")
            return self._get_demo_data(endpoint, params)
    
    def _get_demo_data(self, endpoint: str, params: dict) -> dict:
        """
        Données de démonstration quand pas de clé API
        Parfait pour développer sans dépenser!
        """
        if "standings" in endpoint:
            return {
                "response": [{
                    "league": {
                        "standings": [[
                            {
                                "rank": 1,
                                "team": {
                                    "id": 40,
                                    "name": "Liverpool",
                                    "logo": "https://media.api-sports.io/football/teams/40.png"
                                },
                                "points": 58,
                                "goalsDiff": 32,
                                "form": "WWWDW",
                                "all": {
                                    "played": 24,
                                    "win": 18,
                                    "draw": 4,
                                    "lose": 2,
                                    "goals": {"for": 56, "against": 24}
                                }
                            },
                            {
                                "rank": 2,
                                "team": {
                                    "id": 42,
                                    "name": "Arsenal",
                                    "logo": "https://media.api-sports.io/football/teams/42.png"
                                },
                                "points": 51,
                                "goalsDiff": 22,
                                "form": "WWLDW",
                                "all": {
                                    "played": 24,
                                    "win": 15,
                                    "draw": 6,
                                    "lose": 3,
                                    "goals": {"for": 48, "against": 26}
                                }
                            },
                            {
                                "rank": 3,
                                "team": {
                                    "id": 50,
                                    "name": "Manchester City",
                                    "logo": "https://media.api-sports.io/football/teams/50.png"
                                },
                                "points": 48,
                                "goalsDiff": 19,
                                "form": "WDWWL",
                                "all": {
                                    "played": 24,
                                    "win": 14,
                                    "draw": 6,
                                    "lose": 4,
                                    "goals": {"for": 51, "against": 32}
                                }
                            }
                        ]]
                    }
                }]
            }
        
        elif "fixtures" in endpoint:
            return {
                "response": [
                    {
                        "fixture": {
                            "id": 1001,
                            "date": "2025-02-15T15:00:00+00:00",
                            "venue": {"name": "Anfield"},
                            "status": {"short": "NS"}
                        },
                        "league": {"round": "Matchday 25"},
                        "teams": {
                            "home": {
                                "id": 40,
                                "name": "Liverpool",
                                "logo": "https://media.api-sports.io/football/teams/40.png",
                                "winner": None
                            },
                            "away": {
                                "id": 42,
                                "name": "Arsenal",
                                "logo": "https://media.api-sports.io/football/teams/42.png",
                                "winner": None
                            }
                        },
                        "goals": {"home": None, "away": None}
                    },
                    {
                        "fixture": {
                            "id": 1002,
                            "date": "2025-02-16T17:30:00+00:00",
                            "venue": {"name": "Etihad Stadium"},
                            "status": {"short": "NS"}
                        },
                        "league": {"round": "Matchday 25"},
                        "teams": {
                            "home": {
                                "id": 50,
                                "name": "Manchester City",
                                "logo": "https://media.api-sports.io/football/teams/50.png",
                                "winner": None
                            },
                            "away": {
                                "id": 33,
                                "name": "Manchester United",
                                "logo": "https://media.api-sports.io/football/teams/33.png",
                                "winner": None
                            }
                        },
                        "goals": {"home": None, "away": None}
                    }
                ]
            }
        
        elif "teams/statistics" in endpoint:
            return {
                "response": {
                    "form": "WWDLW",
                    "fixtures": {
                        "played": {"total": 24},
                        "wins": {"total": 14},
                        "draws": {"total": 6},
                        "loses": {"total": 4}
                    },
                    "goals": {
                        "for": {
                            "average": {"total": "2.1"},
                            "total": {"total": 50}
                        },
                        "against": {
                            "average": {"total": "1.2"},
                            "total": {"total": 29}
                        }
                    },
                    "clean_sheet": {"total": 8},
                    "shots": {
                        "total": {"average": "13.5"},
                        "on": {"average": "5.2"}
                    }
                }
            }
        
        elif "players" in endpoint:
            return {
                "response": [{
                    "player": {
                        "id": params.get("id", 0),
                        "name": "Mohamed Salah",
                        "age": 32,
                        "nationality": "Egypt",
                        "photo": "https://media.api-sports.io/football/players/306.png"
                    },
                    "statistics": [{
                        "team": {"name": "Liverpool"},
                        "games": {
                            "appearences": 22,
                            "minutes": 1890,
                            "rating": "7.98",
                            "position": "Attacker"
                        },
                        "goals": {"total": 18, "assists": 9},
                        "shots": {"total": 68, "on": 38},
                        "passes": {"accuracy": "82"},
                        "dribbles": {"attempts": 45, "success": 28}
                    }]
                }]
            }
        
        return {"response": []}
    
    # ========== PUBLIC METHODS ==========
    
    async def get_standings(self, league_name: str) -> List:
        league_id = self.LEAGUES.get(league_name, {}).get("id", 39)
        data = await self._request(
            "standings",
            {"season": self.season, "league": league_id},
            cache_minutes=30
        )
        try:
            return data["response"][0]["league"]["standings"][0]
        except (KeyError, IndexError):
            return []
    
    async def get_next_matches(
        self, 
        league_name: str, 
        next_n: int = 10
    ) -> List:
        league_id = self.LEAGUES.get(league_name, {}).get("id", 39)
        data = await self._request(
            "fixtures",
            {
                "season": self.season,
                "league": league_id,
                "next": next_n,
                "status": "NS"
            },
            cache_minutes=15
        )
        return data.get("response", [])
    
    async def get_live_matches(
        self, 
        league_name: Optional[str] = None
    ) -> List:
        params = {"live": "all"}
        if league_name:
            lid = self.LEAGUES.get(league_name, {}).get("id")
            if lid:
                params["league"] = lid
        data = await self._request("fixtures", params, cache_minutes=1)
        return data.get("response", [])
    
    async def get_team_statistics(
        self, 
        team_id: int, 
        league_name: str
    ) -> Dict:
        league_id = self.LEAGUES.get(league_name, {}).get("id", 39)
        data = await self._request(
            "teams/statistics",
            {
                "season": self.season,
                "team": team_id,
                "league": league_id
            },
            cache_minutes=60
        )
        return data.get("response", {})
    
    async def get_player_statistics(
        self, 
        player_id: int,
        league_name: str
    ) -> List:
        league_id = self.LEAGUES.get(league_name, {}).get("id", 39)
        data = await self._request(
            "players",
            {
                "id": player_id,
                "season": self.season,
                "league": league_id
            },
            cache_minutes=60
        )
        return data.get("response", [])
    
    async def get_h2h(
        self, 
        team1_id: int, 
        team2_id: int, 
        last: int = 10
    ) -> List:
        data = await self._request(
            "fixtures/headtohead",
            {"h2h": f"{team1_id}-{team2_id}", "last": last},
            cache_minutes=1440  # 24h
        )
        return data.get("response", [])
    
    async def get_top_scorers(self, league_name: str) -> List:
        league_id = self.LEAGUES.get(league_name, {}).get("id", 39)
        data = await self._request(
            "players/topscorers",
            {"season": self.season, "league": league_id},
            cache_minutes=120
        )
        return data.get("response", [])
    
    async def get_match_by_id(self, match_id: int) -> Optional[Dict]:
        data = await self._request(
            "fixtures",
            {"id": match_id},
            cache_minutes=30
        )
        results = data.get("response", [])
        return results[0] if results else None
    
    # ========== HELPERS ==========
    
    def extract_features(self, stats: Dict) -> Dict:
        """Extrait features pour le modèle xG"""
        if not stats:
            return self._default_features()
        
        goals = stats.get("goals", {})
        fixtures = stats.get("fixtures", {})
        shots = stats.get("shots", {})
        form_str = stats.get("form", "WDLWL")
        
        played = fixtures.get("played", {}).get("total", 1) or 1
        
        return {
            "goals_for_avg": float(
                goals.get("for", {}).get("average", {}).get("total", "1.5") or 1.5
            ),
            "goals_against_avg": float(
                goals.get("against", {}).get("average", {}).get("total", "1.2") or 1.2
            ),
            "form_points": self._form_to_points(form_str),
            "form_string": form_str or "WDLWL",
            "shots_avg": float(
                shots.get("total", {}).get("average", "12") or 12
            ),
            "shots_on_target_avg": float(
                shots.get("on", {}).get("average", "4.5") or 4.5
            ),
            "possession_avg": 50.0,
            "clean_sheets_pct": (
                stats.get("clean_sheet", {}).get("total", 0) or 0
            ) / played,
            "wins": fixtures.get("wins", {}).get("total", 0) or 0,
            "played": played
        }
    
    def _default_features(self) -> Dict:
        return {
            "goals_for_avg": 1.5,
            "goals_against_avg": 1.2,
            "form_points": 6,
            "form_string": "WDLWL",
            "shots_avg": 12.0,
            "shots_on_target_avg": 4.5,
            "possession_avg": 50.0,
            "clean_sheets_pct": 0.3,
            "wins": 8,
            "played": 20
        }
    
    def _form_to_points(self, form_str: str) -> int:
        points = 0
        for r in (form_str or "")[-5:]:
            if r == "W": points += 3
            elif r == "D": points += 1
        return points
    
    def summarize_h2h(
        self, 
        h2h_data: List, 
        home_team_id: int
    ) -> Dict:
        if not h2h_data:
            return {
                "total": 0,
                "home_wins": 0,
                "draws": 0,
                "away_wins": 0
            }
        
        last_10 = h2h_data[-10:]
        home_wins = draws = away_wins = 0
        
        for m in last_10:
            h_id = m.get("teams", {}).get("home", {}).get("id")
            h_score = m.get("goals", {}).get("home") or 0
            a_score = m.get("goals", {}).get("away") or 0
            
            if h_id == home_team_id:
                if h_score > a_score: home_wins += 1
                elif h_score == a_score: draws += 1
                else: away_wins += 1
            else:
                if a_score > h_score: home_wins += 1
                elif h_score == a_score: draws += 1
                else: away_wins += 1
        
        return {
            "total": len(last_10),
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins
        }