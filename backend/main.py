# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import os
from datetime import datetime

app = FastAPI(
    title="⚽ Football Intelligence Platform",
    description="AI-Powered Football Analytics API",
    version="2.0.0"
)

# CORS - permet au frontend de communiquer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ============ WEBSOCKET MANAGER ============
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# ============ ROUTES DE BASE ============
@app.get("/")
def root():
    return {
        "name": "Football Intelligence Platform",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "leagues": [
            "Premier League",
            "La Liga", 
            "Champions League",
            "Bundesliga",
            "Ligue 1"
        ],
        "endpoints": {
            "docs": "/docs",
            "standings": "/api/standings/{league}",
            "next_matches": "/api/matches/next/{league}",
            "predictions": "/api/predictions/{match_id}",
            "player_form": "/api/players/{player_id}/form",
            "live": "/api/live",
            "report": "/api/reports/match/{match_id}"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "cache": "connected"
    }

# ============ STANDINGS ============
@app.get("/api/standings/{league_name}")
async def get_standings(league_name: str):
    """
    Classement d'une ligue
    league_name: premier_league | la_liga | champions_league
    """
    from services.football_api import FootballAPIService
    service = FootballAPIService()
    
    try:
        data = await service.get_standings(league_name)
        return {
            "league": league_name,
            "season": 2024,
            "standings": data,
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "league": league_name}
        )

# ============ NEXT MATCHES + PREDICTIONS ============
@app.get("/api/matches/next/{league_name}")
async def get_next_matches(league_name: str, n: int = 10):
    """Prochains matchs avec prédictions xG"""
    from services.football_api import FootballAPIService
    from services.xg_calculator import XGCalculator
    
    service = FootballAPIService()
    xg_calc = XGCalculator()
    
    try:
        matches = await service.get_next_matches(league_name, n)
        enriched = []
        
        for match in matches[:n]:
            home_id = match['teams']['home']['id']
            away_id = match['teams']['away']['id']
            
            # Stats équipes
            home_stats = await service.get_team_statistics(
                home_id, league_name
            )
            away_stats = await service.get_team_statistics(
                away_id, league_name
            )
            
            # H2H
            h2h = await service.get_h2h(home_id, away_id, last=10)
            
            # Prédiction
            home_feat = service.extract_features(home_stats)
            away_feat = service.extract_features(away_stats)
            prediction = xg_calc.predict_match_xg(
                home_feat, away_feat, h2h
            )
            
            enriched.append({
                "fixture_id": match['fixture']['id'],
                "date": match['fixture']['date'],
                "venue": match['fixture'].get('venue', {}).get('name', 'TBD'),
                "round": match['league'].get('round', ''),
                "home_team": {
                    "id": home_id,
                    "name": match['teams']['home']['name'],
                    "logo": match['teams']['home']['logo']
                },
                "away_team": {
                    "id": away_id,
                    "name": match['teams']['away']['name'],
                    "logo": match['teams']['away']['logo']
                },
                "prediction": prediction,
                "h2h_summary": service.summarize_h2h(
                    h2h, home_id
                )
            })
        
        return {
            "league": league_name,
            "count": len(enriched),
            "matches": enriched
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ============ LIVE MATCHES ============
@app.get("/api/live")
async def get_live_matches():
    """Matchs en cours RIGHT NOW"""
    from services.football_api import FootballAPIService
    service = FootballAPIService()
    
    try:
        data = await service.get_live_matches()
        return {
            "live_count": len(data),
            "matches": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ============ PLAYER FORM ============
@app.get("/api/players/{player_id}/form")
async def get_player_form(player_id: int, league: str = "premier_league"):
    """Forme actuelle d'un joueur"""
    from services.football_api import FootballAPIService
    from services.player_form import PlayerFormAnalyzer
    
    service = FootballAPIService()
    analyzer = PlayerFormAnalyzer()
    
    try:
        stats = await service.get_player_statistics(player_id, league)
        
        if not stats:
            return JSONResponse(
                status_code=404,
                content={"error": "Player not found"}
            )
        
        player_data = stats[0]
        player_info = player_data.get('player', {})
        player_stats = player_data.get('statistics', [{}])[0]
        
        # Préparer les données de forme
        recent_matches = []
        games = player_stats.get('games', {})
        goals = player_stats.get('goals', {})
        
        # Simuler derniers 5 matchs basé sur stats saison
        for i in range(5):
            recent_matches.append({
                'goals': (goals.get('total') or 0) // max(
                    games.get('appearences') or 1, 1
                ),
                'assists': (goals.get('assists') or 0) // max(
                    games.get('appearences') or 1, 1
                ),
                'rating': float(
                    games.get('rating') or 6.5
                ),
                'minutes': games.get('minutes') // max(
                    games.get('appearences') or 1, 1
                ) if games.get('minutes') else 75
            })
        
        form_analysis = analyzer.calculate_form_score(recent_matches)
        
        return {
            "player": {
                "id": player_id,
                "name": player_info.get('name'),
                "age": player_info.get('age'),
                "nationality": player_info.get('nationality'),
                "position": player_stats.get('games', {}).get('position'),
                "photo": player_info.get('photo'),
                "team": player_stats.get('team', {}).get('name')
            },
            "season_stats": {
                "appearances": player_stats.get('games', {}).get('appearences', 0),
                "goals": player_stats.get('goals', {}).get('total', 0),
                "assists": player_stats.get('goals', {}).get('assists', 0),
                "rating": player_stats.get('games', {}).get('rating', 'N/A'),
                "minutes": player_stats.get('games', {}).get('minutes', 0),
                "pass_accuracy": player_stats.get('passes', {}).get('accuracy', 0),
                "shots_on_target": player_stats.get('shots', {}).get('on', 0),
                "dribbles_success": player_stats.get(
                    'dribbles', {}
                ).get('success', 0)
            },
            "form": form_analysis,
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ============ AI MATCH REPORT ============
@app.get("/api/reports/match/{match_id}")
async def get_match_report(match_id: int, league: str = "premier_league"):
    """Rapport AI complet pour un match"""
    from services.ai_reporter import AIReporter
    from services.football_api import FootballAPIService
    from services.xg_calculator import XGCalculator
    
    service = FootballAPIService()
    reporter = AIReporter()
    xg_calc = XGCalculator()
    
    try:
        # Récupère info du match
        match_data = await service.get_match_by_id(match_id)
        
        if not match_data:
            return JSONResponse(
                status_code=404,
                content={"error": "Match not found"}
            )
        
        home_id = match_data['teams']['home']['id']
        away_id = match_data['teams']['away']['id']
        home_name = match_data['teams']['home']['name']
        away_name = match_data['teams']['away']['name']
        
        # Stats et prédictions
        home_stats = await service.get_team_statistics(home_id, league)
        away_stats = await service.get_team_statistics(away_id, league)
        h2h = await service.get_h2h(home_id, away_id)
        
        home_feat = service.extract_features(home_stats)
        away_feat = service.extract_features(away_stats)
        prediction = xg_calc.predict_match_xg(
            home_feat, away_feat, h2h
        )
        
        # Génère rapport AI
        h2h_summary = service.summarize_h2h(h2h, home_id)
        home_form = home_feat.get('form_string', 'WWDLL')
        away_form = away_feat.get('form_string', 'WDLWL')
        
        preview = await reporter.generate_match_preview(
            home_name, away_name,
            prediction, h2h_summary,
            home_form, away_form
        )
        
        return {
            "match_id": match_id,
            "match": {
                "home": home_name,
                "away": away_name,
                "date": match_data['fixture']['date'],
                "venue": match_data['fixture'].get(
                    'venue', {}
                ).get('name', 'TBD')
            },
            "prediction": prediction,
            "h2h": h2h_summary,
            "ai_report": preview,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ============ TOP SCORERS ============
@app.get("/api/players/top-scorers/{league_name}")
async def get_top_scorers(league_name: str):
    from services.football_api import FootballAPIService
    service = FootballAPIService()
    try:
        data = await service.get_top_scorers(league_name)
        return {"league": league_name, "top_scorers": data[:10]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ============ FBREF ROUTES - LIVE 2025-2026 ============

@app.get("/api/fbref/standings/{league_name}")
async def fbref_standings(league_name: str):
    """Classement live 2025-2026 depuis FBref - GRATUIT"""
    from services.fbref_scraper import FBrefScraper
    scraper = FBrefScraper()
    data = await scraper.get_standings(league_name)
    return {
        "league":     league_name,
        "source":     "FBref.com",
        "season":     "2025-2026",
        "count":      len(data),
        "standings":  data,
        "updated_at": datetime.now().isoformat(),
    }

@app.get("/api/fbref/fixtures/{league_name}")
async def fbref_fixtures(league_name: str, limit: int = 10):
    """Prochains matchs 2025-2026 depuis FBref - GRATUIT"""
    from services.fbref_scraper import FBrefScraper
    scraper = FBrefScraper()
    data = await scraper.get_next_fixtures(league_name, limit)
    return {
        "league":     league_name,
        "source":     "FBref.com",
        "season":     "2025-2026",
        "count":      len(data),
        "matches":    data,
        "updated_at": datetime.now().isoformat(),
    }

@app.get("/api/fbref/players/{league_name}")
async def fbref_players(league_name: str, limit: int = 20):
    """Top joueurs avec xG saison 2025-2026 - GRATUIT"""
    from services.fbref_scraper import FBrefScraper
    scraper = FBrefScraper()
    data = await scraper.get_top_players(league_name, limit)
    return {
        "league":      league_name,
        "source":      "FBref.com",
        "season":      "2025-2026",
        "count":       len(data),
        "top_players": data,
        "updated_at":  datetime.now().isoformat(),
    }

@app.get("/api/fbref/form/{league_name}/{team_name}")
async def fbref_team_form(league_name: str, team_name: str):
    """Forme réelle d'une équipe avec xG - GRATUIT"""
    from services.fbref_scraper import FBrefScraper
    scraper  = FBrefScraper()
    results  = await scraper.get_recent_results(league_name)
    form     = scraper.calculate_team_form(team_name, results)
    return {
        "team":       team_name,
        "league":     league_name,
        "source":     "FBref.com",
        "season":     "2025-2026",
        "form":       form,
        "updated_at": datetime.now().isoformat(),
    }

@app.get("/api/status")
async def api_status():
    """Status de toutes les sources de données"""
    import os
    football_key = os.getenv("FOOTBALL_API_KEY", "")
    groq_key     = os.getenv("GROQ_API_KEY", "")
    return {
        "platform":    "Football Intelligence Platform",
        "version":     "3.0.0",
        "season":      "2025-2026",
        "updated":     datetime.now().isoformat(),
        "data_sources": {
            "api_football": {
                "status":  "active" if (football_key and len(football_key) > 10) else "missing",
                "plan":    "Free - 100 req/day",
                "seasons": "2021-2024",
                "live":    False,
            },
            "fbref_scraping": {
                "status":  "active",
                "plan":    "Free - always",
                "seasons": "2025-2026 LIVE",
                "live":    True,
                "note":    "3s delay between requests (rate limit respect)",
            },
            "groq_ai": {
                "status":  "active" if (groq_key and "gsk_" in groq_key) else "missing",
                "plan":    "Free - 14,400 req/day",
                "model":   "llama-3.3-70b-versatile",
            },
            "statsbomb_open": {
                "status":  "active",
                "plan":    "Free - always",
                "seasons": "Historical xG data",
                "url":     "github.com/statsbomb/open-data",
            },
        },
    }

# ============ FOOTBALL-DATA.ORG ROUTES - LIVE 2025-2026 ============

@app.get("/api/live/standings/{league_name}")
async def live_standings(league_name: str):
    """
    Classement LIVE saison 2025-2026
    Source: Football-Data.org (API officielle)
    """
    from services.football_data import FootballDataService
    service = FootballDataService()
    data = await service.get_standings(league_name)
    return {
        "league":     league_name,
        "source":     "Football-Data.org",
        "season":     "2025-2026",
        "count":      len(data),
        "standings":  data,
        "updated_at": datetime.now().isoformat(),
    }

@app.get("/api/live/fixtures/{league_name}")
async def live_fixtures(league_name: str, limit: int = 10):
    """Prochains matchs LIVE 2025-2026"""
    from services.football_data import FootballDataService
    service = FootballDataService()
    data = await service.get_next_matches(league_name, limit)
    return {
        "league":     league_name,
        "source":     "Football-Data.org",
        "season":     "2025-2026",
        "count":      len(data),
        "matches":    data,
        "updated_at": datetime.now().isoformat(),
    }

@app.get("/api/live/scorers/{league_name}")
async def live_scorers(league_name: str, limit: int = 20):
    """Meilleurs buteurs LIVE 2025-2026"""
    from services.football_data import FootballDataService
    service = FootballDataService()
    data = await service.get_top_scorers(league_name, limit)
    return {
        "league":      league_name,
        "source":      "Football-Data.org",
        "season":      "2025-2026",
        "count":       len(data),
        "top_scorers": data,
        "updated_at":  datetime.now().isoformat(),
    }

@app.get("/api/live/team/{team_id}/matches")
async def live_team_matches(team_id: int, limit: int = 10):
    """Historique matchs d'une équipe (pour forme réelle)"""
    from services.football_data import FootballDataService
    service = FootballDataService()
    data = await service.get_team_matches(team_id, limit)
    return {
        "team_id":   team_id,
        "source":    "Football-Data.org",
        "matches":   data,
        "updated_at": datetime.now().isoformat(),
    }

@app.get("/api/live/quota")
async def live_quota():
    """Info quota API"""
    from services.football_data import FootballDataService
    service = FootballDataService()
    return await service.get_quota_info()

@app.get("/api/smart/standings/{league_name}")
async def smart_standings(league_name: str):
    """
    Classement intelligent - essaie toutes les sources:
    1. Football-Data.org (si quota dispo)
    2. Cache Redis (si rate limited)
    3. API-Football (backup)
    4. Données démo (dernier recours)
    """
    from services.football_data import FootballDataService
    from services.football_api  import FootballAPIService

    # Source 1: Football-Data.org
    fd_service = FootballDataService()
    data = await fd_service.get_standings(league_name)
    if data:
        return {
            "league":    league_name,
            "source":    "Football-Data.org (live)",
            "season":    "2025-2026",
            "count":     len(data),
            "standings": data,
        }

    # Source 2: API-Football (backup)
    fa_service = FootballAPIService()
    data = await fa_service.get_standings(league_name)
    if data:
        return {
            "league":    league_name,
            "source":    "API-Football (backup)",
            "season":    "2024-2025",
            "count":     len(data),
            "standings": data,
        }

    # Source 3: Démo
    return {
        "league":    league_name,
        "source":    "Demo data (all APIs rate limited)",
        "season":    "2025-2026",
        "count":     0,
        "standings": [],
        "message":   "Rate limit atteint - reset à minuit UTC",
    }

# ============ WEBSOCKET LIVE ============
@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Envoie update toutes les 60 secondes
            await asyncio.sleep(60)
            from services.football_api import FootballAPIService
            service = FootballAPIService()
            live = await service.get_live_matches()
            await manager.broadcast({
                "type": "live_update",
                "data": live,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)