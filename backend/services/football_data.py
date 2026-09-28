
# backend/services/football_data.py
# Football-Data.org - Code 1 + Cache Redis optimisé du Code 2
# Classements, fixtures, buteurs, matchs des équipes
# Cache Redis persistant + mémoire + gestion rate limit

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx


class FootballDataService:
    """
    Football-Data.org API v4
    Cache Redis + mémoire
    Gestion du quota et du rate limit
    """

    BASE_URL = "https://api.football-data.org/v4"

    # Compétitions du Code 1
    COMPETITIONS = {
        "premier_league":   "PL",
        "la_liga":          "PD",
        "champions_league": "CL",
        "bundesliga":       "BL1",
        "serie_a":          "SA",
        "ligue_1":          "FL1",
        "eredivisie":       "DED",
        "primeira_liga":    "PPL",
    }

    # Cache en secondes
    CACHE_TTL = {
        "standings": 21600,  # 6 heures
        "fixtures":   3600,  # 1 heure
        "scorers":    7200,  # 2 heures
        "matches":   86400,  # 24 heures
    }

    TEAM_NAME_MAP = {
        "Liverpool FC": "Liverpool",
        "Manchester City FC": "Manchester City",
        "Manchester United FC": "Man United",
        "Arsenal FC": "Arsenal",
        "Chelsea FC": "Chelsea",
        "Tottenham Hotspur FC": "Tottenham",
        "Newcastle United FC": "Newcastle",
        "Aston Villa FC": "Aston Villa",
        "West Ham United FC": "West Ham",
        "Everton FC": "Everton",
        "Real Madrid CF": "Real Madrid",
        "FC Barcelona": "Barcelona",
        "Club Atlético de Madrid": "Atletico Madrid",
        "Sevilla FC": "Sevilla",
        "Real Betis Balompié": "Real Betis",
        "FC Bayern München": "Bayern Munich",
        "Borussia Dortmund": "Dortmund",
        "RB Leipzig": "RB Leipzig",
        "Bayer 04 Leverkusen": "Leverkusen",
        "Paris Saint-Germain FC": "PSG",
        "Olympique de Marseille": "Marseille",
        "AS Monaco FC": "Monaco",
        "Olympique Lyonnais": "Lyon",
        "Juventus FC": "Juventus",
        "FC Internazionale Milano": "Inter Milan",
        "AC Milan": "AC Milan",
        "SSC Napoli": "Napoli",
        "AS Roma": "Roma",
    }

    def __init__(self):
        self.token = os.getenv("FOOTBALL_DATA_TOKEN", "")
        self._mem_cache: Dict[str, tuple] = {}

        self.headers = {
            "X-Auth-Token": self.token,
            "Accept": "application/json",
        }

        # Redis optionnel
        self._redis = None
        self._use_redis = False

        try:
            import redis

            self._redis = redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._redis.ping()
            self._use_redis = True
            print("✅ Redis cache connecté")
        except Exception as exc:
            print(f"⚠️ Redis indisponible: {exc}")
            print("📦 Cache mémoire uniquement")

        has_token = (
            bool(self.token)
            and len(self.token) > 10
            and "ta_cle" not in self.token
        )

        print(
            f"{'✅' if has_token else '❌'} "
            f"FOOTBALL_DATA_TOKEN: "
            f"{'SET' if has_token else 'MISSING'}"
        )

    # ==========================================
    # CACHE
    # ==========================================

    def _cache_key(self, endpoint: str) -> str:
        return hashlib.md5(endpoint.encode()).hexdigest()

    def _get_cache(
        self,
        key: str,
        ttl: int
    ) -> Optional[dict]:
        # 1. Redis persistant
        if self._use_redis:
            try:
                raw = self._redis.get(f"fip:{key}")
                if raw is not None:
                    print(f"📦 Redis hit: {key[:12]}")
                    return json.loads(raw)
            except Exception as exc:
                print(f"⚠️ Redis read error: {exc}")

        # 2. Cache mémoire
        if key in self._mem_cache:
            data, timestamp = self._mem_cache[key]

            age = (
                datetime.now(timezone.utc) - timestamp
            ).total_seconds()

            if age < ttl:
                print(f"📦 Memory hit: {key[:12]}")
                return data

            del self._mem_cache[key]

        return None

    def _set_cache(
        self,
        key: str,
        data: dict,
        ttl: int
    ):
        # Redis
        if self._use_redis:
            try:
                self._redis.setex(
                    f"fip:{key}",
                    ttl,
                    json.dumps(data, ensure_ascii=False),
                )
            except Exception as exc:
                print(f"⚠️ Redis write error: {exc}")

        # Mémoire
        self._mem_cache[key] = (
            data,
            datetime.now(timezone.utc),
        )

    # ==========================================
    # HTTP + CACHE + RATE LIMIT
    # ==========================================

    async def _get(
        self,
        endpoint: str,
        cache_type: str = "standings",
    ) -> Dict:
        if not self.token or "ta_cle" in self.token:
            print("❌ Token API absent ou invalide")
            return {}

        key = self._cache_key(endpoint)
        ttl = self.CACHE_TTL.get(cache_type, 3600)

        # Cache d'abord
        cached = self._get_cache(key, ttl)

        if cached is not None:
            if cached.get("_rate_limited"):
                print("⚠️ API temporairement limitée")
                return {}
            return cached

        # Appel API
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/{endpoint}",
                    headers=self.headers,
                )

            print(
                f"🌐 API: {endpoint[:60]} "
                f"→ {response.status_code}"
            )

            if response.status_code == 429:
                print("⚠️ Rate limit 429 - pause 1h")

                self._set_cache(
                    key,
                    {"_rate_limited": True},
                    3600,
                )
                return {}

            if response.status_code == 403:
                print(
                    "❌ HTTP 403 - "
                    "Compétition non accessible"
                )
                return {}

            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}")
                return {}

            data = response.json()

            if not isinstance(data, dict):
                print("❌ Format API inattendu")
                return {}

            self._set_cache(key, data, ttl)
            return data

        except httpx.TimeoutException:
            print(f"⏱️ Timeout API: {endpoint}")
            return {}

        except Exception as exc:
            print(f"❌ Request error: {exc}")
            return {}

    # ==========================================
    # STANDINGS
    # ==========================================

    async def get_standings(
        self,
        league_name: str
    ) -> List[Dict]:
        code = self.COMPETITIONS.get(league_name, "PL")

        data = await self._get(
            f"competitions/{code}/standings",
            cache_type="standings",
        )

        if not data or data.get("_rate_limited"):
            return []

        total_table = None

        for standing in data.get("standings", []):
            if standing.get("type") == "TOTAL":
                total_table = standing.get("table", [])
                break

        if not total_table:
            return []

        standings = []

        for i, row in enumerate(total_table):
            team_raw = row.get("team", {})

            raw_name = (
                team_raw.get("shortName")
                or team_raw.get("name", "Unknown")
            )

            team_name = self.TEAM_NAME_MAP.get(
                raw_name,
                raw_name,
            )

            crest = team_raw.get("crest", "") or (
                "https://ui-avatars.com/api/"
                f"?name={'+'.join(team_name.split())}"
                "&background=1a2035"
                "&color=00d4aa&bold=true&size=64"
            )

            played = row.get("playedGames", 0)
            won = row.get("won", 0)
            drawn = row.get("draw", 0)
            lost = row.get("lost", 0)
            gf = row.get("goalsFor", 0)
            ga = row.get("goalsAgainst", 0)
            pts = row.get("points", 0)

            standings.append({
                "rank": row.get("position", i + 1),
                "team": {
                    "id": team_raw.get("id", i + 1),
                    "name": team_name,
                    "logo": crest,
                },
                "points": pts,
                "goalsDiff": row.get(
                    "goalDifference", gf - ga
                ),
                "form": self._estimate_form(
                    won, drawn, lost
                ),
                "all": {
                    "played": played,
                    "win": won,
                    "draw": drawn,
                    "lose": lost,
                    "goals": {
                        "for": gf,
                        "against": ga,
                    },
                },
                "goals_for_avg": round(
                    gf / max(played, 1), 2
                ),
                "goals_against_avg": round(
                    ga / max(played, 1), 2
                ),
                "form_points": won * 3 + drawn,
                "clean_sheets_pct": 0.0,
                "source": "Football-Data.org",
                "season": "2025-2026",
            })

        print(
            f"✅ Standings {league_name}: "
            f"{len(standings)} teams"
        )
        return standings

    # ==========================================
    # FIXTURES - PROCHAINS MATCHS
    # ==========================================

    async def get_next_matches(
        self,
        league_name: str,
        limit: int = 10,
    ) -> List[Dict]:
        code = self.COMPETITIONS.get(league_name, "PL")

        data = await self._get(
            f"competitions/{code}/matches",
            cache_type="fixtures",
        )

        if not data or data.get("_rate_limited"):
            return []

        matches_raw = data.get("matches", [])
        now = datetime.now(timezone.utc)
        fixtures = []

        for match in matches_raw:
            status = match.get("status", "")

            if status not in ["SCHEDULED", "TIMED"]:
                continue

            utc_date = match.get("utcDate", "")

            try:
                match_dt = datetime.fromisoformat(
                    utc_date.replace("Z", "+00:00")
                )
                if match_dt.tzinfo is None:
                    match_dt = match_dt.replace(
                        tzinfo=timezone.utc
                    )
            except (ValueError, AttributeError):
                continue

            if match_dt < now:
                continue

            home_raw = match.get("homeTeam", {})
            away_raw = match.get("awayTeam", {})

            home_name_raw = (
                home_raw.get("shortName")
                or home_raw.get("name", "Home")
            )
            away_name_raw = (
                away_raw.get("shortName")
                or away_raw.get("name", "Away")
            )

            home_name = self.TEAM_NAME_MAP.get(
                home_name_raw, home_name_raw
            )
            away_name = self.TEAM_NAME_MAP.get(
                away_name_raw, away_name_raw
            )

            fixtures.append({
                "fixture_id": match.get("id", 0),
                "date": match_dt.isoformat(),
                "date_human": match_dt.strftime(
                    "%a %d %b %Y %H:%M"
                ),
                "venue": match.get("venue") or "TBD",
                "round": (
                    f"Matchday {match.get('matchday', '?')}"
                ),
                "status": status,
                "home_team": {
                    "id": home_raw.get("id", 0),
                    "name": home_name,
                    "logo": home_raw.get("crest") or (
                        "https://ui-avatars.com/api/"
                        f"?name={'+'.join(home_name.split())}"
                        "&background=1a2035"
                        "&color=00d4aa&bold=true&size=64"
                    ),
                },
                "away_team": {
                    "id": away_raw.get("id", 0),
                    "name": away_name,
                    "logo": away_raw.get("crest") or (
                        "https://ui-avatars.com/api/"
                        f"?name={'+'.join(away_name.split())}"
                        "&background=0f3460"
                        "&color=e94560&bold=true&size=64"
                    ),
                },
                "source": "Football-Data.org",
                "season": "2025-2026",
            })

            if len(fixtures) >= limit:
                break

        print(
            f"✅ Fixtures {league_name}: "
            f"{len(fixtures)} upcoming"
        )
        return fixtures

    # ==========================================
    # TOP SCORERS
    # ==========================================

    async def get_top_scorers(
        self,
        league_name: str,
        limit: int = 20,
    ) -> List[Dict]:
        code = self.COMPETITIONS.get(league_name, "PL")

        data = await self._get(
            f"competitions/{code}/scorers",
            cache_type="scorers",
        )

        if not data or data.get("_rate_limited"):
            return []

        players = []

        for scorer in data.get("scorers", [])[:limit]:
            player = scorer.get("player", {})
            team = scorer.get("team", {})

            goals = scorer.get("goals", 0) or 0
            assists = scorer.get("assists", 0) or 0
            penalties = scorer.get("penalties", 0) or 0

            raw_team_name = (
                team.get("shortName")
                or team.get("name", "N/A")
            )

            team_name = self.TEAM_NAME_MAP.get(
                raw_team_name,
                raw_team_name,
            )

            players.append({
                "player_id": player.get("id", 0),
                "name": player.get("name", "Unknown"),
                "nationality": player.get(
                    "nationality", "N/A"
                ),
                "position": player.get(
                    "position", "N/A"
                ),
                "team": team_name,
                "team_id": team.get("id", 0),
                "goals": goals,
                "assists": assists,
                "penalties": penalties,
                "goal_contributions": goals + assists,
                "open_play_goals": goals - penalties,
                "source": "Football-Data.org",
                "season": "2025-2026",
            })

        print(
            f"✅ Scorers {league_name}: "
            f"{len(players)} players"
        )
        return players

    # ==========================================
    # TEAM MATCHES
    # ==========================================

    async def get_team_matches(
        self,
        team_id: int,
        limit: int = 10,
    ) -> List[Dict]:
        data = await self._get(
            f"teams/{team_id}/matches",
            cache_type="matches",
        )

        if not data or data.get("_rate_limited"):
            return []

        matches = []

        for match in data.get("matches", []):
            if match.get("status") != "FINISHED":
                continue

            score = match.get("score", {})
            full_time = score.get("fullTime", {})

            home_goals = full_time.get("home")
            away_goals = full_time.get("away")

            if home_goals is None or away_goals is None:
                continue

            matches.append({
                "date": match.get("utcDate", ""),
                "home_team": match.get(
                    "homeTeam", {}
                ).get("name", ""),
                "away_team": match.get(
                    "awayTeam", {}
                ).get("name", ""),
                "home_score": home_goals,
                "away_score": away_goals,
                "matchday": match.get("matchday", 0),
                "competition": match.get(
                    "competition", {}
                ).get("name", ""),
                "source": "Football-Data.org",
            })

            if len(matches) >= limit:
                break

        return matches

    # ==========================================
    # FORME ESTIMÉE - CODE 1
    # ==========================================

    def _estimate_form(
        self,
        won: int,
        drawn: int,
        lost: int,
    ) -> str:
        total = won + drawn + lost

        if total == 0:
            return "-----"

        ratio = won / total

        if ratio >= 0.75:
            return "WWWWW"
        elif ratio >= 0.55:
            return "WWWDW"
        elif ratio >= 0.40:
            return "WDWLD"
        elif ratio >= 0.25:
            return "WDLWL"
        else:
            return "LLWDL"

    # ==========================================
    # QUOTA INFO
    # ==========================================

    async def get_quota_info(self) -> Dict:
        return {
            "plan": "Free",
            "limit_per_day": 50,
            "cache": {
                "standings": "6 heures",
                "fixtures": "1 heure",
                "scorers": "2 heures",
                "matches": "24 heures",
            },
            "redis_enabled": self._use_redis,
            "note": (
                "Cache Redis persistant avec "
                "fallback mémoire"
            ),
            "recommendation": (
                "Surveiller les appels API "
                "et les réponses HTTP 429"
            ),
        }