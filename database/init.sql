-- database/init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- LEAGUES
CREATE TABLE IF NOT EXISTS leagues (
    id SERIAL PRIMARY KEY,
    api_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    logo_url TEXT,
    season INTEGER DEFAULT 2024,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- TEAMS
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    api_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(20),
    country VARCHAR(50),
    logo_url TEXT,
    founded INTEGER,
    stadium VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- PLAYERS
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    api_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    nationality VARCHAR(50),
    position VARCHAR(30),
    photo_url TEXT,
    team_id INTEGER REFERENCES teams(id),
    market_value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- MATCHES
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    api_id INTEGER UNIQUE NOT NULL,
    league_id INTEGER REFERENCES leagues(id),
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    match_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'NS',
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    venue VARCHAR(100),
    referee VARCHAR(100),
    round VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- MATCH STATISTICS
CREATE TABLE IF NOT EXISTS match_statistics (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    team_id INTEGER REFERENCES teams(id),
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    possession DECIMAL(5,2) DEFAULT 0,
    passes_total INTEGER DEFAULT 0,
    passes_accurate INTEGER DEFAULT 0,
    pass_accuracy DECIMAL(5,2) DEFAULT 0,
    fouls INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    corners INTEGER DEFAULT 0,
    xg DECIMAL(6,3) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- XG PREDICTIONS
CREATE TABLE IF NOT EXISTS xg_predictions (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    home_xg DECIMAL(6,3),
    away_xg DECIMAL(6,3),
    home_win_prob DECIMAL(5,3),
    draw_prob DECIMAL(5,3),
    away_win_prob DECIMAL(5,3),
    predicted_score VARCHAR(10),
    confidence DECIMAL(5,3),
    features JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- STANDINGS
CREATE TABLE IF NOT EXISTS standings (
    id SERIAL PRIMARY KEY,
    league_id INTEGER REFERENCES leagues(id),
    team_id INTEGER REFERENCES teams(id),
    season INTEGER DEFAULT 2024,
    rank INTEGER,
    played INTEGER DEFAULT 0,
    win INTEGER DEFAULT 0,
    draw INTEGER DEFAULT 0,
    lose INTEGER DEFAULT 0,
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    goal_diff INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    form VARCHAR(20),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(league_id, team_id, season)
);

-- PLAYER FORM
CREATE TABLE IF NOT EXISTS player_form (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    match_id INTEGER REFERENCES matches(id),
    rating DECIMAL(4,2),
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    minutes INTEGER DEFAULT 0,
    form_score DECIMAL(5,2),
    match_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI REPORTS
CREATE TABLE IF NOT EXISTS ai_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50),
    entity_id INTEGER,
    entity_type VARCHAR(30),
    content TEXT,
    match_id INTEGER,
    model_used VARCHAR(50) DEFAULT 'llama-3.1-70b',
    created_at TIMESTAMP DEFAULT NOW()
);

-- INSERT DEFAULT LEAGUES
INSERT INTO leagues (api_id, name, country, season) VALUES
(39,  'Premier League',    'England', 2024),
(140, 'La Liga',           'Spain',   2024),
(2,   'Champions League',  'Europe',  2024),
(61,  'Ligue 1',           'France',  2024),
(78,  'Bundesliga',        'Germany', 2024)
ON CONFLICT (api_id) DO NOTHING;

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_matches_date 
    ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_league 
    ON matches(league_id);
CREATE INDEX IF NOT EXISTS idx_standings_league 
    ON standings(league_id, season);
CREATE INDEX IF NOT EXISTS idx_player_form 
    ON player_form(player_id);
CREATE INDEX IF NOT EXISTS idx_xg_match 
    ON xg_predictions(match_id);