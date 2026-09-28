<div align="center">

<img src="https://img.shields.io/badge/⚽-Football%20Intelligence%20Platform-00d4aa?style=for-the-badge&labelColor=0a0e1a" alt="FIP"/>

# Football Intelligence Platform

### AI-Powered Football Analytics | La Liga · Premier League · Champions League

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![n8n](https://img.shields.io/badge/n8n-Automation-EA4B71?style=flat-square&logo=n8n&logoColor=white)](https://n8n.io)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

<br/>

> **Real-time football analytics platform** combining Machine Learning,  
> AI-generated reports, and live data from 6 major leagues.  
> Built for the **2025-2026 season** — data updated every hour.

<br/>

![Platform Preview](docs/preview.png)

**[Live Demo](https://football-intelligence.demo.com)** ·
**[API Docs](https://football-intelligence.demo.com/docs)** ·
**[Report Bug](https://github.com/yourusername/football-intelligence/issues)**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#️-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Configuration](#️-configuration)
- [API Reference](#-api-reference)
- [Data Sources](#-data-sources)
- [ML Models](#-ml-models)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [Business Value](#-business-value)
- [Author](#-author)

---

## 🎯 Overview

Football Intelligence Platform is a **production-ready analytics system**
that aggregates live football data from multiple sources, applies Machine
Learning models for Expected Goals (xG) prediction, and delivers insights
through a modern React dashboard and REST API.

The Problem:
├── Scouts spend 40+ hours/week watching matches manually
├── Report generation takes 3-4 hours per match
├── Subjective analysis leads to costly transfer mistakes

The Solution:
├── Automated data collection every hour (24/7)
├── AI-generated match reports in 30 seconds
├── Objective ML-based xG models (ROC-AUC: 0.81)
└── Real-time alerts via WhatsApp/Email (n8n automation)

---

## ✨ Features

### 📊 Live Data Dashboard

| Feature           | Description                | Status  |
| ----------------- | -------------------------- | ------- |
| League Standings  | Real-time 2025-2026 tables | ✅ Live |
| Upcoming Fixtures | Next 10 matches per league | ✅ Live |
| Top Scorers       | Goals, assists, penalties  | ✅ Live |
| Live Match Scores | Real-time score updates    | ✅ Live |
| Player Form Index | Custom 0-100 form score    | ✅ Live |

### 🤖 AI & Machine Learning

| Feature          | Description                | Status    |
| ---------------- | -------------------------- | --------- |
| xG Predictions   | Expected Goals per match   | ✅ Active |
| Win Probability  | Poisson distribution model | ✅ Active |
| Score Predictor  | Most likely scorelines     | ✅ Active |
| AI Match Reports | LLaMA 3.3 70B analysis     | ✅ Active |
| Player Scouting  | Automated scout reports    | ✅ Active |

### 🔄 Automation (n8n)

| Feature           | Description               | Status    |
| ----------------- | ------------------------- | --------- |
| Hourly Data Sync  | Auto-refresh all leagues  | ✅ Active |
| WhatsApp Alerts   | Pre-match notifications   | ✅ Active |
| Daily PDF Reports | Auto-generated summaries  | ✅ Active |
| Email Digest      | Morning football briefing | ✅ Active |

---

## 🏗️ Architecture

┌─────────────────────────────────────────────────────────────┐
│ FOOTBALL INTELLIGENCE PLATFORM │
│ Season 2025-2026 │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ React 18 │ FastAPI │ ML Engine │ n8n │
│ TypeScript │ Python │ Scikit-learn │ Automation │
│ Dashboard │ REST API │ xG Models │ Workflows │
├──────────────┴──────────────┴──────────────┴───────────────┤
│ PostgreSQL 15 + Redis 7 │
│ (Persistent storage + Smart cache) │
├─────────────────────────────────────────────────────────────┤
│ EXTERNAL DATA SOURCES │
│ Football-Data.org │ API-Football │ FBref │ StatsBomb Open │
│ (Live 2025-26) │ (Historical) │ (xG) │ (ML Training) │
└─────────────────────────────────────────────────────────────┘

---

### Data Flow

Live Match Event
│
▼
Football-Data.org API (official)
│
├──► PostgreSQL (persist)
├──► Redis Cache (6h TTL)
├──► ML Engine (xG calc)
└──► Groq AI (reports)
│
▼
React Dashboard
│
▼
n8n Automation
(alerts & reports)

---

## 🛠 Tech Stack

### Backend

FastAPI 0.115 → REST API + WebSocket
Python 3.11 → Core language
PostgreSQL 15 → Primary database
Redis 7 → Cache layer (smart TTL)
SQLAlchemy 2.0 → ORM
httpx → Async HTTP client
BeautifulSoup4 → Web scraping fallback
SciPy → Poisson distribution

### Frontend

React 18 → UI framework
TypeScript → Type safety
CSS Variables → Dark theme design system

### Machine Learning

Scikit-learn → xG model (Gradient Boosting)
SciPy → Poisson distribution
NumPy / Pandas → Data processing
StatsBomb Open → Training data (professional-grade)

### Infrastructure

Docker Compose → Container orchestration
n8n → Workflow automation
Redis → Smart API cache
PostgreSQL → Data persistence

### AI / LLM

Groq API → LLaMA 3.3 70B
14,400 requests/day free

---

## 🚀 Quick Start

# 1. Clone

git clone https://github.com/yourusername/football-intelligence.git
cd football-intelligence

# 2. Configure

cp .env.example .env

# Edit .env → add FOOTBALL_DATA_TOKEN and GROQ_API_KEY

# 3. Launch

docker-compose up -d

# 4. Open (wait 30 seconds first)

# Dashboard: http://localhost:3000

# API Docs: http://localhost:8000/docs

# n8n: http://localhost:5679

Verify
Bash

curl http://localhost:8000/api/status
curl http://localhost:8000/api/live/standings/premier_league

⚙️ Configuration

# Required API Keys (Both Free)

FOOTBALL_DATA_TOKEN=your_token # football-data.org → free 50 req/day
GROQ_API_KEY=gsk_your_key # console.groq.com → free 14k req/day

# Get Football-Data.org Token (2 minutes)

1. https://www.football-data.org/client/register
2. Register with email (free, instant)
3. Confirm email
4. Login → copy API Token

# Get Groq API Key (1 minute)

1. https://console.groq.com
2. Sign in with Google
3. API Keys → Create API Key
4. Copy (starts with gsk\_...)

# Full .env Reference

DB_USER=admin
DB_PASSWORD=football2026secure
DB_NAME=football_intelligence
REDIS_PASSWORD=redis2026secure
FOOTBALL_DATA_TOKEN= ← Required
FOOTBALL_API_KEY= ← Optional backup
GROQ_API_KEY= ← Required for AI
FOOTBALL_SEASON=2025
SECRET_KEY=your-secret-min-32-chars
GRAFANA_PASSWORD=grafana2026

📡 API Reference

# Endpoints

# System

GET / → Platform info
GET /api/status → Data sources status
GET /health → Health check

# Live Data 2025-2026

GET /api/live/standings/{league} → Current standings
GET /api/live/fixtures/{league} → Upcoming matches
GET /api/live/scorers/{league} → Top scorers
GET /api/live/team/{team_id}/matches → Team matches

# Predictions

GET /api/matches/next/{league} → Fixtures + xG predictions
GET /api/predictions/{match_id} → Full match prediction

# Players

GET /api/players/{player_id}/form → Form score 0-100

# AI

GET /api/reports/match/{match_id} → AI match preview

# Leagues

premier_league England Premier League
la_liga Spanish La Liga
champions_league UEFA Champions League
bundesliga German Bundesliga
serie_a Italian Serie A
ligue_1 French Ligue 1
Sample Response
JSON

{
"league": "premier_league",
"source": "Football-Data.org",
"season": "2025-2026",
"count": 20,
"standings": [
{
"rank": 1,
"team": { "name": "Man City", "logo": "https://..." },
"points": 15,
"goalsDiff": 8,
"all": { "played": 5, "win": 5, "draw": 0, "lose": 0,
"goals": { "for": 14, "against": 6 } },
"goals_for_avg": 2.8,
"source": "Football-Data.org",
"season": "2025-2026"
}
]
}

📊 Data Sources

SOURCE DATA COST FRESHNESS
─────────────────────────────────────────────────────────
Football-Data.org Live 2025-26 Free Real-time
API-Football Historical Free 2021-2024
FBref.com xG + Advanced Free Live (slow)
StatsBomb Open ML Training Free Historical
Groq LLaMA 3.3 AI Reports Free On-demand
─────────────────────────────────────────────────────────

Smart Fallback:
Football-Data.org → API-Football → FBref → Demo Data

# Cache Strategy

Type TTL Max calls/day Quota saved
──────────────────────────────────────────────────
Standings 6 hours 4 96%
Fixtures 1 hour 24 83%
Scorers 2 hours 12 91%

🤖 ML Models

# Expected Goals (xG)

Algorithm: Gradient Boosting Classifier
Training: StatsBomb Open Data (10,000+ shots)
ROC-AUC: 0.81 (industry: 0.75-0.85)

Features:
├── Distance to goal
├── Shot angle
├── Header / foot
├── Direct free kick
├── Defenders nearby
└── Counter-attack

Output:
├── xG per shot (0.01-0.99)
├── Team xG for/against
└── Win probabilities (Poisson)

# Player Form Index

Range: 0 - 100

Scoring:
├── Goals × 15 pts (max 30)
├── Assists × 8 pts (max 15)
├── Rating × 7 pts (base 6.0)
├── Minutes (penalty if < 60)
└── Cards (-10 yellow / -30 red)

Categories:
🔥 80-100 Excellent
✅ 65-79 Good
😐 50-64 Average
⚠️ 35-49 Poor
❌ 0-34 Very Poor

📁 Project Structure

football-intelligence/
│
├── docker-compose.yml ← Start everything
├── .env ← API keys (never commit!)
├── .env.example ← Setup template
├── .gitignore
├── README.md
│
├── backend/
│ ├── Dockerfile
│ ├── requirements.txt
│ ├── main.py ← FastAPI + all routes
│ └── services/
│ ├── football_data.py ← Live 2025-2026 data
│ ├── football_api.py ← Historical backup
│ ├── fbref_scraper.py ← Free scraping
│ ├── xg_calculator.py ← ML predictions
│ ├── player_form.py ← Form scoring
│ └── ai_reporter.py ← Groq AI reports
│
├── frontend/
│ ├── Dockerfile
│ ├── package.json
│ ├── tsconfig.json
│ └── src/
│ ├── App.tsx ← Main dashboard
│ └── styles/globals.css
│
├── database/
│ └── init.sql ← PostgreSQL schema
│
└── n8n-workflows/
└── football_pipeline.json ← Automation

🗺 Roadmap

✅ v1.0 - September 2026 (Current)

Live standings 6 leagues
Upcoming fixtures
Top scorers
xG prediction model (AUC 0.81)
AI match reports (Groq LLaMA 3.3)
Smart Redis cache
Docker full stack
n8n automation

🔜 v1.1 - October 2026

xG charts on fixture cards
Player form on match preview
H2H visualization
Mobile responsive

🔮 v2.0 - Q1 2027

Injury tracker
Lineup predictor
WhatsApp bot
PDF scouting reports
Prediction accuracy history

🔧 Useful Commands

# Start

docker-compose up -d

# Stop

docker-compose down

# Rebuild backend

docker-compose build --no-cache backend
docker-compose up -d

# View logs

docker-compose logs -f backend

# Flush cache (force refresh)

docker exec fip-redis redis-cli -a redis2026secure FLUSHDB

# Check quota

curl http://localhost:8000/api/live/quota

# Database access

docker exec -it fip-postgres psql -U admin -d football_intelligence

# All services status

docker-compose ps

📄 License

MIT License — free for learning and portfolio use.

👤 Author

Ossamix-Dev
Data Analyst

<div align="center">
⭐ Star this repo if it helped you!

"Bringing data science to the beautiful game"

FastAPI · React · PostgreSQL · Redis · Docker · n8n · Groq AI · scikit-learn

</div> '@
