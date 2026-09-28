<div align="center">

# ⚽ Football Platform

### AI-Powered Football Analytics | Premier League · La Liga · Champions League

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**Real-time football analytics platform - Season 2025-2026**

[API Docs](http://localhost:8000/docs) · [n8n](http://localhost:5679) · [Issues](https://github.com/midasoda-arch/football-intelligence/issues)

</div>

---

## What This Does

Aggregates live football data, applies ML xG models, and delivers insights through a React dashboard.

- Live standings, fixtures, scorers (Premier League, La Liga, UCL, Bundesliga)
- Expected Goals (xG) predictions with Poisson probabilities
- AI match reports powered by Groq LLaMA 3.3 70B
- Smart Redis cache to manage API quotas
- n8n automation for alerts and reports

---

## Quick Start

### Requirements

- Docker Desktop
- Git
- 8GB RAM minimum

### Install

\\\ash
git clone https://github.com/midasoda-arch/football-intelligence.git
cd football-intelligence
cp .env.example .env
\\\

Edit \.env\ and add your API keys:

\\\env
FOOTBALL_DATA_TOKEN=your_token_here
GROQ_API_KEY=gsk_your_key_here
\\\

\\\ash
docker-compose up -d
\\\

Open:

- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs
- n8n: http://localhost:5679

---

## Get API Keys (Both Free)

**Football-Data.org** (live 2025-2026 data):

1. Go to https://www.football-data.org/client/register
2. Register with email
3. Login and copy your API Token

**Groq** (AI reports):

1. Go to https://console.groq.com
2. Sign in with Google
3. API Keys → Create → Copy (starts with gsk\_...)

---

## Architecture

\\\
React 18 (Dashboard)
|
FastAPI (Python Backend)
|
+-- PostgreSQL 15 (Database)
+-- Redis 7 (Smart Cache)
+-- ML Engine (xG Model)
+-- Groq AI (Match Reports)
|
+-- Football-Data.org (Live 2025-26)
+-- API-Football (Historical)
+-- FBref (Scraping fallback)
+-- StatsBomb Open (ML Training)

n8n (Automation - alerts, reports, sync)
\\\

---

## API Endpoints

\\\
GET /api/status System status
GET /api/live/standings/{league} Live standings
GET /api/live/fixtures/{league} Upcoming matches
GET /api/live/scorers/{league} Top scorers
GET /api/matches/next/{league} Fixtures + xG predictions
GET /api/players/{player_id}/form Player form (0-100)
GET /api/reports/match/{match_id} AI match report
\\\

**Leagues:**
\\\
premier_league la_liga champions_league
bundesliga serie_a ligue_1
\\\

---

## ML Model - Expected Goals (xG)

- Algorithm: Gradient Boosting Classifier
- Training data: StatsBomb Open Data (10,000+ shots)
- Performance: ROC-AUC = 0.81
- Method: Poisson distribution for match probabilities

**Features used:** distance, angle, header/foot, free kick, defenders nearby, counter-attack

**Output:** xG per shot, win/draw/loss probabilities, top 5 likely scorelines

---

## Player Form Index

Custom scoring system (0-100):

| Component    | Points        |
| ------------ | ------------- |
| Goal         | +15 (max 30)  |
| Assist       | +8 (max 15)   |
| Rating       | ×7 (base 6.0) |
| Minutes < 60 | penalty       |
| Yellow card  | -10           |
| Red card     | -30           |

Categories: 🔥 Excellent (80+) · ✅ Good (65+) · 😐 Average (50+) · ⚠️ Poor (35+) · ❌ Very Poor

---

## Data Sources

| Source            | Data          | Cost | Freshness  |
| ----------------- | ------------- | ---- | ---------- |
| Football-Data.org | Live 2025-26  | Free | Real-time  |
| API-Football      | Historical    | Free | 2021-2024  |
| FBref.com         | xG + Advanced | Free | Live       |
| StatsBomb Open    | ML Training   | Free | Historical |
| Groq LLaMA 3.3    | AI Reports    | Free | On-demand  |

**Smart fallback:** Football-Data.org → API-Football → FBref → Demo

**Cache TTL:** Standings 6h · Fixtures 1h · Scorers 2h

---

## Project Structure

\\\
football-intelligence/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│ ├── Dockerfile
│ ├── requirements.txt
│ ├── main.py
│ └── services/
│ ├── football_data.py Live data
│ ├── football_api.py Backup API
│ ├── fbref_scraper.py Free scraping
│ ├── xg_calculator.py ML predictions
│ ├── player_form.py Form scoring
│ └── ai_reporter.py Groq AI
├── frontend/
│ ├── Dockerfile
│ ├── package.json
│ └── src/
│ ├── App.tsx
│ └── styles/globals.css
├── database/
│ └── init.sql
└── n8n-workflows/
└── football_pipeline.json
\\\

---

## Commands

\\\ash

# Start

docker-compose up -d

# Stop

docker-compose down

# Rebuild backend

docker-compose build --no-cache backend
docker-compose up -d

# View logs

docker-compose logs -f backend

# Flush cache

docker exec fip-redis redis-cli -a redis2026secure FLUSHDB

# Check status

docker-compose ps
\\\

---

## Roadmap

- [x] Live standings 6 leagues (2025-2026)
- [x] Upcoming fixtures
- [x] Top scorers
- [x] xG prediction model (AUC 0.81)
- [x] AI match reports
- [x] Smart Redis cache
- [x] Docker full stack
- [x] n8n automation
- [ ] xG charts on fixture cards
- [ ] Player form on match preview
- [ ] Mobile responsive design
- [ ] WhatsApp bot integration
- [ ] PDF scouting reports
- [ ] Prediction accuracy tracking

---

## License

MIT License

---

## Author

**Ossamix-Dev**
Data Analyst

[![GitHub](https://img.shields.io/badge/GitHub-midasoda--arch-181717?style=flat-square&logo=github)](https://github.com/midasoda-arch)
[![Email](https://img.shields.io/badge/Email-Contact-EA4335?style=flat-square&logo=gmail)](mailto:midasoda1@gmail.com)

---

<div align="center">

_Bringing data science to the beautiful game_

**Star this repo if it helped you ⭐**

</div>
