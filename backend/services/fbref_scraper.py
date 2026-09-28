# backend/services/fbref_scraper.py
# FBref Scraper 2025-2026 - Données Live Gratuites
# Septembre 2026 - Saison 2025/2026 en cours

import httpx
import asyncio
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

class FBrefScraper:
    """
    Scraper FBref.com - 100% gratuit
    Saison courante: 2025-2026
    Données: Standings, Fixtures, Players, xG
    
    FBref = source officielle utilisée par:
    - The Guardian, BBC Sport, Sky Sports
    - Opta, StatsBomb pour vérification
    """

    # URLs saison 2025-2026 (mises à jour Sept 2026)
    LEAGUE_URLS = {
        "premier_league": {
            "standings": "https://fbref.com/en/comps/9/Premier-League-Stats",
            "fixtures":  "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures",
            "players":   "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
            "name":      "Premier League",
        },
        "la_liga": {
            "standings": "https://fbref.com/en/comps/12/La-Liga-Stats",
            "fixtures":  "https://fbref.com/en/comps/12/schedule/La-Liga-Scores-and-Fixtures",
            "players":   "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
            "name":      "La Liga",
        },
        "champions_league": {
            "standings": "https://fbref.com/en/comps/8/Champions-League-Stats",
            "fixtures":  "https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures",
            "players":   "https://fbref.com/en/comps/8/stats/Champions-League-Stats",
            "name":      "Champions League",
        },
        "bundesliga": {
            "standings": "https://fbref.com/en/comps/20/Bundesliga-Stats",
            "fixtures":  "https://fbref.com/en/comps/20/schedule/Bundesliga-Scores-and-Fixtures",
            "players":   "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
            "name":      "Bundesliga",
        },
        "serie_a": {
            "standings": "https://fbref.com/en/comps/11/Serie-A-Stats",
            "fixtures":  "https://fbref.com/en/comps/11/schedule/Serie-A-Scores-and-Fixtures",
            "players":   "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
            "name":      "Serie A",
        },
        "ligue_1": {
            "standings": "https://fbref.com/en/comps/13/Ligue-1-Stats",
            "fixtures":  "https://fbref.com/en/comps/13/schedule/Ligue-1-Scores-and-Fixtures",
            "players":   "https://fbref.com/en/comps/13/stats/Ligue-1-Stats",
            "name":      "Ligue 1",
        },
    }

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cache-Control":   "no-cache",
        "Referer":         "https://www.google.com/",
    }

    def __init__(self):
        self._cache: Dict[str, Tuple] = {}
        self.current_season = "2025-2026"
        print(f"✅ FBref Scraper initialized | Season: {self.current_season}")

    # ─────────────────────────────────────────────────
    #  CACHE
    # ─────────────────────────────────────────────────
    def _cached(self, key: str, ttl_min: int = 60) -> Optional[object]:
        if key in self._cache:
            data, ts = self._cache[key]
            if (datetime.now() - ts).seconds < ttl_min * 60:
                return data
        return None

    def _store(self, key: str, data: object):
        self._cache[key] = (data, datetime.now())

    # ─────────────────────────────────────────────────
    #  HTTP FETCH
    # ─────────────────────────────────────────────────
    async def _fetch(self, url: str, ttl_min: int = 60) -> Optional[BeautifulSoup]:
        """
        Récupère et parse une page FBref.
        Rate-limit: attend 3s entre chaque appel (respecte FBref).
        """
        ck = hashlib.md5(url.encode()).hexdigest()
        cached = self._cached(ck, ttl_min)
        if cached:
            return cached

        try:
            await asyncio.sleep(3)  # Respecte le rate limit FBref
            async with httpx.AsyncClient(
                headers=self.HEADERS,
                follow_redirects=True,
                timeout=45.0,
            ) as client:
                resp = await client.get(url)

            if resp.status_code == 429:
                print("⚠️  FBref rate limit - waiting 60s...")
                await asyncio.sleep(60)
                async with httpx.AsyncClient(
                    headers=self.HEADERS,
                    follow_redirects=True,
                    timeout=45.0,
                ) as client:
                    resp = await client.get(url)

            if resp.status_code != 200:
                print(f"❌ FBref HTTP {resp.status_code} for {url}")
                return None

            soup = BeautifulSoup(resp.text, "lxml")
            self._store(ck, soup)
            return soup

        except Exception as exc:
            print(f"❌ FBref fetch error: {exc}")
            return None

    # ─────────────────────────────────────────────────
    #  HELPER: int safe
    # ─────────────────────────────────────────────────
    @staticmethod
    def _int(td) -> int:
        if td is None:
            return 0
        txt = td.get_text(strip=True).replace(",", "")
        try:
            return int(float(txt))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _float(td) -> float:
        if td is None:
            return 0.0
        txt = td.get_text(strip=True).replace(",", "")
        try:
            return float(txt)
        except (ValueError, TypeError):
            return 0.0

    # ─────────────────────────────────────────────────
    #  STANDINGS 2025-2026
    # ─────────────────────────────────────────────────
    async def get_standings(self, league_name: str) -> List[Dict]:
        """
        Classement en temps réel saison 2025-2026.
        Inclut xG pour et contre (données premium gratuites sur FBref!).
        """
        urls = self.LEAGUE_URLS.get(league_name)
        if not urls:
            return self._demo_standings()

        ck = f"standings_{league_name}"
        cached = self._cached(ck, ttl_min=30)
        if cached:
            return cached

        soup = await self._fetch(urls["standings"], ttl_min=30)
        if not soup:
            return self._demo_standings()

        standings = []

        # FBref a plusieurs tables - prend la table "overall"
        # Cherche par data-stat présents dans les headers
        tables = soup.find_all("table", class_=re.compile("stats_table"))

        target_table = None
        for tbl in tables:
            # La table standings a "rank" et "points" et "team"
            headers = [th.get("data-stat", "") for th in tbl.find_all("th")]
            if "rank" in headers and "points" in headers and "team" in headers:
                target_table = tbl
                break

        if not target_table:
            # Fallback: prend la première table avec tbody
            target_table = soup.find("table", class_=re.compile("stats_table"))

        if not target_table:
            print(f"❌ No standings table found for {league_name}")
            return self._demo_standings()

        tbody = target_table.find("tbody")
        if not tbody:
            return self._demo_standings()

        rank = 0
        for row in tbody.find_all("tr"):
            # Skip header rows dans tbody
            if row.get("class") and "thead" in row.get("class", []):
                continue

            team_td = row.find("td", {"data-stat": "team"})
            if not team_td:
                continue

            rank += 1
            team_name = team_td.get_text(strip=True)
            if not team_name:
                continue

            # Récupère chaque stat
            mp  = self._int(row.find("td", {"data-stat": "games"}))
            w   = self._int(row.find("td", {"data-stat": "wins"}))
            d   = self._int(row.find("td", {"data-stat": "ties"}))
            lo  = self._int(row.find("td", {"data-stat": "losses"}))
            gf  = self._int(row.find("td", {"data-stat": "goals_for"}))
            ga  = self._int(row.find("td", {"data-stat": "goals_against"}))
            pts = self._int(row.find("td", {"data-stat": "points"}))
            xg  = self._float(row.find("td", {"data-stat": "xg_for"}))
            xga = self._float(row.find("td", {"data-stat": "xg_against"}))

            # Logo via ui-avatars (toujours dispo)
            logo = (
                f"https://ui-avatars.com/api/"
                f"?name={'+'.join(team_name.split())}"
                f"&background=1a2035&color=00d4aa&bold=true&size=64"
            )

            standings.append({
                "rank":      rank,
                "team":      {"id": rank, "name": team_name, "logo": logo},
                "points":    pts,
                "goalsDiff": gf - ga,
                "form":      "-----",
                "xg":        round(xg, 2),
                "xga":       round(xga, 2),
                "xg_diff":   round(xg - xga, 2),
                "all": {
                    "played": mp,
                    "win":    w,
                    "draw":   d,
                    "lose":   lo,
                    "goals":  {"for": gf, "against": ga},
                },
                "source":  "FBref.com",
                "season":  self.current_season,
            })

        if not standings:
            print(f"❌ Parsed 0 teams for {league_name}")
            return self._demo_standings()

        print(f"✅ FBref standings: {len(standings)} teams ({league_name})")
        self._store(ck, standings)
        return standings

    # ─────────────────────────────────────────────────
    #  FIXTURES - Prochains matchs 2025-2026
    # ─────────────────────────────────────────────────
    async def get_next_fixtures(
        self,
        league_name: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Prochains matchs non joués saison 2025-2026.
        Filtre: seulement les matchs FUTURS (date > aujourd'hui).
        """
        urls = self.LEAGUE_URLS.get(league_name)
        if not urls:
            return self._demo_fixtures()

        ck = f"fixtures_{league_name}"
        cached = self._cached(ck, ttl_min=15)
        if cached:
            return cached

        soup = await self._fetch(urls["fixtures"], ttl_min=15)
        if not soup:
            return self._demo_fixtures()

        table = soup.find("table", class_=re.compile("stats_table"))
        if not table:
            return self._demo_fixtures()

        fixtures  = []
        now       = datetime.now()

        for row in table.find_all("tr"):
            if row.get("class") and "thead" in row.get("class", []):
                continue

            date_td  = row.find("td", {"data-stat": "date"})
            time_td  = row.find("td", {"data-stat": "time"})
            home_td  = row.find("td", {"data-stat": "home_team"})
            away_td  = row.find("td", {"data-stat": "away_team"})
            score_td = row.find("td", {"data-stat": "score"})
            venue_td = row.find("td", {"data-stat": "venue"})
            round_td = row.find("td", {"data-stat": "gameweek"}) or \
                       row.find("td", {"data-stat": "round"})

            if not all([date_td, home_td, away_td]):
                continue

            # Score vide = match pas encore joué
            score_txt = score_td.get_text(strip=True) if score_td else ""
            if score_txt and score_txt not in ["", "–", "-", " "]:
                continue

            date_str = date_td.get_text(strip=True)
            time_str = time_td.get_text(strip=True) if time_td else "15:00"

            try:
                # FBref format: "2025-09-28"
                match_dt = datetime.strptime(date_str, "%Y-%m-%d")
                # Ajoute l'heure si disponible
                try:
                    h, m  = time_str.split(":")
                    match_dt = match_dt.replace(hour=int(h), minute=int(m))
                except (ValueError, AttributeError):
                    pass
            except ValueError:
                continue

            # Seulement les matchs futurs
            if match_dt < now:
                continue

            home_name = home_td.get_text(strip=True)
            away_name = away_td.get_text(strip=True)
            venue     = venue_td.get_text(strip=True) if venue_td else "TBD"
            gameweek  = round_td.get_text(strip=True) if round_td else ""

            if not home_name or not away_name:
                continue

            fix_id = abs(hash(f"{date_str}{home_name}{away_name}")) % 999999

            fixtures.append({
                "fixture_id": fix_id,
                "date":       match_dt.isoformat(),
                "date_human": match_dt.strftime("%a %d %b %Y %H:%M"),
                "venue":      venue,
                "round":      gameweek or self.current_season,
                "home_team": {
                    "id":   abs(hash(home_name)) % 9999,
                    "name": home_name,
                    "logo": (
                        f"https://ui-avatars.com/api/"
                        f"?name={'+'.join(home_name.split())}"
                        f"&background=1a2035&color=00d4aa&bold=true&size=64"
                    ),
                },
                "away_team": {
                    "id":   abs(hash(away_name)) % 9999,
                    "name": away_name,
                    "logo": (
                        f"https://ui-avatars.com/api/"
                        f"?name={'+'.join(away_name.split())}"
                        f"&background=0f3460&color=e94560&bold=true&size=64"
                    ),
                },
                "source": "FBref.com",
                "season": self.current_season,
            })

            if len(fixtures) >= limit:
                break

        if not fixtures:
            print(f"❌ No upcoming fixtures found for {league_name}")
            return self._demo_fixtures()

        print(f"✅ FBref fixtures: {len(fixtures)} upcoming ({league_name})")
        self._store(ck, fixtures)
        return fixtures

    # ─────────────────────────────────────────────────
    #  TOP PLAYERS avec xG
    # ─────────────────────────────────────────────────
    async def get_top_players(
        self,
        league_name: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Stats joueurs saison 2025-2026.
        Inclut: buts, passes D, xG, xA, minutes.
        """
        urls = self.LEAGUE_URLS.get(league_name)
        if not urls:
            return []

        ck = f"players_{league_name}"
        cached = self._cached(ck, ttl_min=120)
        if cached:
            return cached

        soup = await self._fetch(urls["players"], ttl_min=120)
        if not soup:
            return []

        # Table stats standard
        table = soup.find("table", id=re.compile("stats_standard"))
        if not table:
            tables = soup.find_all("table", class_=re.compile("stats_table"))
            table  = tables[0] if tables else None

        if not table:
            return []

        players = []
        for row in table.find_all("tr"):
            if row.get("class") and "thead" in row.get("class", []):
                continue

            player_td = row.find("td", {"data-stat": "player"})
            if not player_td:
                continue

            name      = player_td.get_text(strip=True)
            team_td   = row.find("td", {"data-stat": "team"})
            nation_td = row.find("td", {"data-stat": "nationality"})
            pos_td    = row.find("td", {"data-stat": "position"})
            age_td    = row.find("td", {"data-stat": "age"})
            mp_td     = row.find("td", {"data-stat": "games"})
            min_td    = row.find("td", {"data-stat": "minutes"})
            goals_td  = row.find("td", {"data-stat": "goals"})
            ast_td    = row.find("td", {"data-stat": "assists"})
            xg_td     = row.find("td", {"data-stat": "xg"})
            xa_td     = row.find("td", {"data-stat": "xg_assist"})
            shots_td  = row.find("td", {"data-stat": "shots"})

            if not name:
                continue

            goals   = self._int(goals_td)
            assists = self._int(ast_td)

            # Filtre: au moins 1 contribution
            if goals + assists == 0:
                continue

            xg  = self._float(xg_td)
            xa  = self._float(xa_td)
            mp  = self._int(mp_td)
            mins = self._int(min_td)

            # Calcule performance vs attendu
            xg_overperformance = round(goals - xg, 2) if xg > 0 else 0.0

            players.append({
                "name":              name,
                "team":              team_td.get_text(strip=True) if team_td else "N/A",
                "nationality":       nation_td.get_text(strip=True) if nation_td else "N/A",
                "position":          pos_td.get_text(strip=True) if pos_td else "N/A",
                "age":               age_td.get_text(strip=True) if age_td else "N/A",
                "appearances":       mp,
                "minutes":           mins,
                "goals":             goals,
                "assists":           assists,
                "goal_contributions": goals + assists,
                "xg":                round(xg, 2),
                "xa":                round(xa, 2),
                "xg_overperformance": xg_overperformance,
                "shots":             self._int(shots_td),
                "goals_per_90":      round(goals / max(mins, 1) * 90, 2),
                "xg_per_90":         round(xg   / max(mins, 1) * 90, 2),
                "source":            "FBref.com",
                "season":            self.current_season,
            })

        # Tri par buts
        players = sorted(players, key=lambda x: x["goals"], reverse=True)[:limit]

        print(f"✅ FBref players: {len(players)} ({league_name})")
        self._store(ck, players)
        return players

    # ─────────────────────────────────────────────────
    #  MATCH RESULTS RÉCENTS (pour forme des équipes)
    # ─────────────────────────────────────────────────
    async def get_recent_results(
        self,
        league_name: str,
        last_n: int = 50
    ) -> List[Dict]:
        """
        Résultats récents avec xG réel par match.
        Utilisé pour calculer la forme des équipes.
        """
        urls = self.LEAGUE_URLS.get(league_name)
        if not urls:
            return []

        ck = f"results_{league_name}"
        cached = self._cached(ck, ttl_min=60)
        if cached:
            return cached

        soup = await self._fetch(urls["fixtures"], ttl_min=60)
        if not soup:
            return []

        table   = soup.find("table", class_=re.compile("stats_table"))
        if not table:
            return []

        results = []
        now     = datetime.now()

        for row in table.find_all("tr"):
            if row.get("class") and "thead" in row.get("class", []):
                continue

            date_td  = row.find("td", {"data-stat": "date"})
            home_td  = row.find("td", {"data-stat": "home_team"})
            away_td  = row.find("td", {"data-stat": "away_team"})
            score_td = row.find("td", {"data-stat": "score"})
            xg_h_td  = row.find("td", {"data-stat": "xg"})
            xg_a_td  = row.find("td", {"data-stat": "xg_opp"})

            if not all([date_td, home_td, away_td, score_td]):
                continue

            score_txt = score_td.get_text(strip=True)
            if not score_txt or score_txt in ["", "–", "-"]:
                continue  # Match pas encore joué

            date_str = date_td.get_text(strip=True)
            try:
                match_dt = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            if match_dt > now:
                continue  # Futur

            # Parse le score "2–1"
            try:
                parts  = re.split(r"[–\-]", score_txt)
                home_g = int(parts[0].strip())
                away_g = int(parts[1].strip())
            except (ValueError, IndexError):
                continue

            results.append({
                "date":      match_dt.isoformat(),
                "home_team": home_td.get_text(strip=True),
                "away_team": away_td.get_text(strip=True),
                "home_score": home_g,
                "away_score": away_g,
                "home_xg":   self._float(xg_h_td),
                "away_xg":   self._float(xg_a_td),
                "source":    "FBref.com",
            })

            if len(results) >= last_n:
                break

        print(f"✅ FBref results: {len(results)} recent ({league_name})")
        self._store(ck, results)
        return results

    # ─────────────────────────────────────────────────
    #  FORM CALCULATOR depuis les résultats réels
    # ─────────────────────────────────────────────────
    def calculate_team_form(
        self,
        team_name: str,
        results: List[Dict],
        last_n: int = 5
    ) -> Dict:
        """
        Calcule la forme réelle d'une équipe
        depuis les résultats FBref.
        """
        team_results = []
        for r in results:
            is_home = r["home_team"] == team_name
            is_away = r["away_team"] == team_name
            if not (is_home or is_away):
                continue

            if is_home:
                gf, ga = r["home_score"], r["away_score"]
                xg_for, xg_ag = r["home_xg"], r["away_xg"]
                opponent = r["away_team"]
            else:
                gf, ga = r["away_score"], r["home_score"]
                xg_for, xg_ag = r["away_xg"], r["home_xg"]
                opponent = r["home_team"]

            result = "W" if gf > ga else ("D" if gf == ga else "L")
            team_results.append({
                "date":     r["date"],
                "opponent": opponent,
                "gf": gf, "ga": ga,
                "xg_for": xg_for, "xg_ag": xg_ag,
                "result":   result,
            })

        last5 = team_results[-last_n:]
        form_str = "".join(r["result"] for r in last5)
        pts_earned = sum(3 if r["result"] == "W" else 1 if r["result"] == "D" else 0 for r in last5)
        avg_xg_for = sum(r["xg_for"] for r in last5) / max(len(last5), 1)
        avg_xg_ag  = sum(r["xg_ag"] for r in last5) / max(len(last5), 1)

        return {
            "team":          team_name,
            "form_string":   form_str,
            "form_points":   pts_earned,
            "form_max":      len(last5) * 3,
            "avg_xg_for":    round(avg_xg_for, 2),
            "avg_xg_against": round(avg_xg_ag, 2),
            "last_5_results": last5,
            "season":        self.current_season,
        }

    # ─────────────────────────────────────────────────
    #  DEMO DATA
    # ─────────────────────────────────────────────────
    def _demo_standings(self) -> List[Dict]:
        teams = [
            ("Liverpool",        64, 35, 20, 4, 2,  62, 27, 3.12, 0.95),
            ("Arsenal",          58, 26, 17, 7, 3,  55, 29, 2.45, 1.12),
            ("Manchester City",  52, 18, 15, 7, 5,  49, 31, 2.18, 1.34),
            ("Chelsea",          48, 14, 14, 6, 7,  44, 30, 1.98, 1.45),
            ("Tottenham",        43,  9, 12, 7, 8,  38, 29, 1.76, 1.67),
            ("Aston Villa",      41,  7, 11, 8, 8,  35, 28, 1.65, 1.55),
            ("Newcastle",        38,  5, 10, 8, 9,  31, 26, 1.45, 1.34),
            ("Man United",       32, -2,  8, 8,11,  27, 29, 1.23, 1.78),
            ("West Ham",         30, -4,  8, 6,13,  25, 29, 1.15, 1.89),
            ("Everton",          28, -8,  7, 7,13,  22, 30, 1.02, 1.95),
        ]
        return [
            {
                "rank":      i + 1,
                "team":      {
                    "id":   i + 1,
                    "name": t[0],
                    "logo": (
                        f"https://ui-avatars.com/api/"
                        f"?name={'+'.join(t[0].split())}"
                        f"&background=1a2035&color=00d4aa&bold=true&size=64"
                    ),
                },
                "points":    t[1],
                "goalsDiff": t[2],
                "form":      "WWDLW",
                "xg":        t[8],
                "xga":       t[9],
                "xg_diff":   round(t[8] - t[9], 2),
                "all": {
                    "played": t[3] + t[4] + t[5],
                    "win":    t[3],
                    "draw":   t[4],
                    "lose":   t[5],
                    "goals":  {"for": t[6], "against": t[7]},
                },
                "source":  "Demo (FBref unavailable)",
                "season":  "2025-2026",
            }
            for i, t in enumerate(teams)
        ]

    def _demo_fixtures(self) -> List[Dict]:
        now   = datetime.now()
        games = [
            ("Liverpool",        "Arsenal",           "Anfield",            3),
            ("Manchester City",  "Chelsea",            "Etihad Stadium",     5),
            ("Real Madrid",      "FC Barcelona",       "Santiago Bernabéu",  7),
            ("Bayern Munich",    "Borussia Dortmund",  "Allianz Arena",      9),
            ("PSG",              "Olympique Marseille","Parc des Princes",   11),
        ]
        return [
            {
                "fixture_id":  9000 + i,
                "date":        (now + timedelta(days=d)).isoformat(),
                "date_human":  (now + timedelta(days=d)).strftime("%a %d %b %Y %H:%M"),
                "venue":       venue,
                "round":       f"Matchday {20 + i}",
                "home_team":   {
                    "id":   100 + i, "name": home,
                    "logo": f"https://ui-avatars.com/api/?name={'+'.join(home.split())}&background=1a2035&color=00d4aa&bold=true&size=64",
                },
                "away_team":   {
                    "id":   200 + i, "name": away,
                    "logo": f"https://ui-avatars.com/api/?name={'+'.join(away.split())}&background=0f3460&color=e94560&bold=true&size=64",
                },
                "source":      "Demo (FBref unavailable)",
                "season":      "2025-2026",
            }
            for i, (home, away, venue, d) in enumerate(games)
        ]