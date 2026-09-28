import React, { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// ============ TYPES ============
interface Team {
  rank: number;
  team: { id: number; name: string; logo: string };
  points: number;
  goalsDiff: number;
  form: string;
  all: {
    played: number;
    win: number;
    draw: number;
    lose: number;
    goals: { for: number; against: number };
  };
  goals_for_avg: number;
  goals_against_avg: number;
}

interface Match {
  fixture_id: number;
  date: string;
  date_human: string;
  venue: string;
  round: string;
  home_team: { id: number; name: string; logo: string };
  away_team: { id: number; name: string; logo: string };
}

const LEAGUES = [
  { id: 'premier_league', name: 'Premier League', flag: '🏴' },
  { id: 'la_liga', name: 'La Liga', flag: '🇪🇸' },
  { id: 'champions_league', name: 'Champions League', flag: '⭐' },
  { id: 'bundesliga', name: 'Bundesliga', flag: '🇩🇪' },
];

export default function App() {
  const [league, setLeague] = useState('premier_league');
  const [tab, setTab] = useState<'standings' | 'fixtures' | 'scorers'>('standings');
  const [standings, setStandings] = useState<Team[]>([]);
  const [fixtures, setFixtures] = useState<Match[]>([]);
  const [scorers, setScorers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Charge standings
  useEffect(() => {
    if (tab !== 'standings') return;
    setLoading(true);
    fetch(`${API_URL}/api/live/standings/${league}`)
      .then(r => r.json())
      .then(d => setStandings(d.standings || []))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, [tab, league]);

  // Charge fixtures
  useEffect(() => {
    if (tab !== 'fixtures') return;
    setLoading(true);
    fetch(`${API_URL}/api/live/fixtures/${league}?limit=10`)
      .then(r => r.json())
      .then(d => setFixtures(d.matches || []))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, [tab, league]);

  // Charge scorers
  useEffect(() => {
    if (tab !== 'scorers') return;
    setLoading(true);
    fetch(`${API_URL}/api/live/scorers/${league}?limit=20`)
      .then(r => r.json())
      .then(d => setScorers(d.top_scorers || []))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, [tab, league]);

  return (
    <div className="app">
      {/* HEADER */}
      <header className="header">
        <h1>⚽ Football Intelligence Platform</h1>
        <p>Live Data 2025-2026 | Source: Football-Data.org</p>
      </header>

      {/* LEAGUE TABS */}
      <div className="league-tabs">
        {LEAGUES.map(l => (
          <button
            key={l.id}
            className={`league-tab ${league === l.id ? 'active' : ''}`}
            onClick={() => setLeague(l.id)}
          >
            {l.flag} {l.name}
          </button>
        ))}
      </div>

      {/* VIEW TABS */}
      <div className="view-tabs">
        <button className={tab === 'standings' ? 'active' : ''} onClick={() => setTab('standings')}>
          📊 Classement
        </button>
        <button className={tab === 'fixtures' ? 'active' : ''} onClick={() => setTab('fixtures')}>
          📅 Prochains Matchs
        </button>
        <button className={tab === 'scorers' ? 'active' : ''} onClick={() => setTab('scorers')}>
          ⚽ Buteurs
        </button>
      </div>

      {loading && <div className="loader">⏳ Chargement des données live...</div>}

      {/* STANDINGS */}
      {tab === 'standings' && !loading && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Équipe</th>
                <th>J</th>
                <th>G</th>
                <th>N</th>
                <th>P</th>
                <th>BP</th>
                <th>BC</th>
                <th>+/-</th>
                <th>Pts</th>
                <th>Attaque</th>
                <th>Défense</th>
              </tr>
            </thead>
            <tbody>
              {standings.map(t => (
                <tr key={t.team.id}>
                  <td className={`rank rank-${t.rank <= 4 ? 'cl' : t.rank >= 18 ? 'rel' : 'mid'}`}>
                    {t.rank}
                  </td>
                  <td className="team-cell">
                    <img src={t.team.logo} alt="" width={24} height={24} onError={(e) => {
                      (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${encodeURIComponent(t.team.name)}&background=1a2035&color=00d4aa&size=24`;
                    }} />
                    {t.team.name}
                  </td>
                  <td>{t.all.played}</td>
                  <td>{t.all.win}</td>
                  <td>{t.all.draw}</td>
                  <td>{t.all.lose}</td>
                  <td>{t.all.goals.for}</td>
                  <td>{t.all.goals.against}</td>
                  <td>{t.goalsDiff > 0 ? `+${t.goalsDiff}` : t.goalsDiff}</td>
                  <td className="points">{t.points}</td>
                  <td>{t.goals_for_avg}</td>
                  <td>{t.goals_against_avg}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* FIXTURES */}
      {tab === 'fixtures' && !loading && (
        <div className="matches-grid">
          {fixtures.map(m => (
            <div key={m.fixture_id} className="match-card">
              <div className="match-date">📅 {m.date_human}</div>
              <div className="match-round">{m.round}</div>
              
              <div className="teams-row">
                <div className="team">
                  <img src={m.home_team.logo} alt="" width={40} onError={(e) => {
                    (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${encodeURIComponent(m.home_team.name)}&background=1a2035&color=00d4aa&size=40`;
                  }} />
                  <span>{m.home_team.name}</span>
                </div>
                <div className="vs">VS</div>
                <div className="team">
                  <span>{m.away_team.name}</span>
                  <img src={m.away_team.logo} alt="" width={40} onError={(e) => {
                    (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${encodeURIComponent(m.away_team.name)}&background=0f3460&color=e94560&size=40`;
                  }} />
                </div>
              </div>

              <div className="venue">📍 {m.venue || 'TBD'}</div>
            </div>
          ))}
        </div>
      )}

      {/* SCORERS */}
      {tab === 'scorers' && !loading && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Joueur</th>
                <th>Équipe</th>
                <th>⚽ Buts</th>
                <th>🎯 Passes D</th>
                <th>Total</th>
                <th>Dont penalties</th>
              </tr>
            </thead>
            <tbody>
              {scorers.map((p, i) => (
                <tr key={p.player_id || i}>
                  <td className="rank">{i + 1}</td>
                  <td className="player-name">{p.name}</td>
                  <td>{p.team}</td>
                  <td className="goals">{p.goals}</td>
                  <td>{p.assists}</td>
                  <td className="points">{p.goal_contributions}</td>
                  <td>{p.penalties}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <footer className="footer">
        <p>✅ Données LIVE temps réel | Football-Data.org | Saison 2025-2026</p>
        <p>Backend: FastAPI + PostgreSQL | Frontend: React | Automation: n8n</p>
      </footer>
    </div>
  );
}