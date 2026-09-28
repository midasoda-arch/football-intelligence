# ⚽ Football Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Season](https://img.shields.io/badge/Season-2025--2026-orange?style=flat-square)

**Real-time football analytics · xG predictions · AI reports · Live data**

[Report Bug](https://github.com/midasoda-arch/football-intelligence/issues) · [Request Feature](https://github.com/midasoda-arch/football-intelligence/issues)

</div>

---

## 📌 Overview

> A **production-ready** football analytics platform built for the **2025-2026 season**. Combines live data from official APIs, Machine Learning xG models, and AI-generated match reports — all served through a modern React dashboard and REST API.

Built by a **Data Analyst** passionate about football — covering **Premier League**, **La Liga**, **Champions League**, **Bundesliga**, **Serie A** and **Ligue 1**.

---

## ✨ Key Features

### 📊 Live Data — Season 2025-2026

- ⚡ **Real-time standings** for 6 major leagues, updated hourly
- 📅 **Upcoming fixtures** with dates, venues, matchday info
- ⚽ **Top scorers** with goals, assists, penalties breakdown
- 🧠 **Smart Redis cache** — saves 90%+ of API quota automatically

### 🤖 Machine Learning

- 🎯 **Expected Goals (xG)** — Gradient Boosting model, ROC-AUC **0.81**
- 📈 **Match probabilities** — Poisson distribution (Win/Draw/Loss)
- 🔢 **Top 5 likely scorelines** per fixture
- 💪 **Player Form Index** — custom 0-100 score

### 🧠 AI Reports

- 📝 **Match previews** by **Groq LLaMA 3.3 70B**
- 🔍 **Scout reports** — strengths, weaknesses, recommendation
- 🔑 **Key factors** analysis before each match

### 🔄 Automation — n8n

- 🕐 **Hourly data sync** across all leagues
- 📱 **WhatsApp alerts** 3h before kickoff
- 📄 **Daily PDF reports** via email

---

## 🏗️ Architecture

| Layer           | Component             | Role             |
| --------------- | --------------------- | ---------------- |
| 🖥️ Presentation | React 18 + TypeScript | Dashboard UI     |
| ⚙️ API          | FastAPI (Python 3.11) | REST + WebSocket |
| 🗄️ Storage      | PostgreSQL 15         | Persistence      |
| ⚡ Cache        | Redis 7               | Quota management |
| 🤖 ML           | Scikit-learn + SciPy  | xG + Poisson     |
| 🧠 AI           | Groq LLaMA 3.3 70B    | Text reports     |
| 🔄 Automation   | n8n                   | Workflows        |
| 🐳 Infra        | Docker Compose        | Orchestration    |

**Data flow:** `Sources → FastAPI → PostgreSQL/Redis → ML/AI → React Dashboard → n8n Alerts`

---

## 🚀 Quick Start

### Prerequisites

| Tool           | Version  | Link                                                       |
| -------------- | -------- | ---------------------------------------------------------- |
| Docker Desktop | ≥ 4.x    | [Download](https://www.docker.com/products/docker-desktop) |
| Git            | ≥ 2.x    | [Download](https://git-scm.com)                            |
| RAM            | 8 GB min | —                                                          |

### Installation

**Step 1 — Clone:**

```bash
git clone https://github.com/midasoda-arch/football-intelligence.git
cd football-intelligence
```

**Step 2 — Configure:**

```bash
cp .env.example .env
```

Edit `.env` with your two free API keys:

```env
FOOTBALL_DATA_TOKEN=your_token_here
GROQ_API_KEY=gsk_your_key_here
```

**Step 3 — Launch:**

```bash
docker-compose up -d
```

**Step 4 — Open:**

| Service      | URL                        |
| ------------ | -------------------------- |
| 🖥️ Dashboard | http://localhost:3000      |
| 📡 API Docs  | http://localhost:8000/docs |
| 🔄 n8n       | http://localhost:5679      |

---

## 🔑 Free API Keys Setup

### Football-Data.org — Live 2025-26 Data

1. Register at [football-data.org/client/register](https://www.football-data.org/client/register)
2. Confirm your email
3. Login → copy your **API Token**
4. Free plan: **50 requests/day** (resets midnight UTC)

### Groq — AI Reports

1. Go to [console.groq.com](https://console.groq.com)
2. Sign in with Google
3. **API Keys** → Create → copy key (starts with `gsk_`)
4. Free plan: **14,400 requests/day**

---

## 📡 API Reference

### Supported Leagues

| Code               | League                    |
| ------------------ | ------------------------- |
| `premier_league`   | 🏴 England Premier League |
| `la_liga`          | 🇪🇸 Spanish La Liga        |
| `champions_league` | ⭐ UEFA Champions League  |
| `bundesliga`       | 🇩🇪 German Bundesliga      |
| `serie_a`          | 🇮🇹 Italian Serie A        |
| `ligue_1`          | 🇫🇷 French Ligue 1         |

### Endpoints

```
GET /api/status                          System & sources status
GET /api/live/standings/{league}         Live standings 2025-26
GET /api/live/fixtures/{league}          Upcoming matches
GET /api/live/scorers/{league}           Top scorers
GET /api/matches/next/{league}           Fixtures + xG predictions
GET /api/players/{player_id}/form        Player form score 0-100
GET /api/reports/match/{match_id}        AI match preview
```

### Sample Response

```json
{
  "league": "premier_league",
  "source": "Football-Data.org",
  "season": "2025-2026",
  "standings": [
    {
      "rank": 1,
      "team": { "name": "Man City" },
      "points": 15,
      "all": { "played": 5, "win": 5, "draw": 0, "lose": 0 }
    }
  ]
}
```

---

## 📊 Data Sources

| Source               | Data                         | Cost | Coverage           |
| -------------------- | ---------------------------- | ---- | ------------------ |
| 🟢 Football-Data.org | Standings, Fixtures, Scorers | Free | **2025-2026 Live** |
| 🔵 API-Football      | Historical stats             | Free | 2021-2024          |
| 🟡 FBref.com         | xG advanced metrics          | Free | Fallback           |
| 🟣 StatsBomb Open    | Shot-level xG                | Free | ML training        |
| 🔴 Groq LLaMA 3.3    | AI text generation           | Free | On-demand          |

**Smart Fallback Chain:** Football-Data.org → API-Football → FBref → Demo

### Cache Strategy

| Data Type | TTL | Max Calls/Day | Quota Saved |
| --------- | --- | ------------- | ----------- |
| Standings | 6h  | 4             | 96%         |
| Fixtures  | 1h  | 24            | 83%         |
| Scorers   | 2h  | 12            | 91%         |

---

## 🤖 ML Models

### Expected Goals (xG)

| Property  | Value                                  |
| --------- | -------------------------------------- |
| Algorithm | Gradient Boosting Classifier           |
| Training  | StatsBomb Open Data (10,000+ shots)    |
| ROC-AUC   | **0.81** (industry: 0.75-0.85)         |
| Method    | Poisson distribution for probabilities |

**Features:** distance, angle, body part, situation (open play/free kick/corner), defenders nearby, counter-attack phase

**Output:** xG per team, W/D/L probabilities, top 5 scorelines, confidence score

### Player Form Index (0-100)

| Score     | Category  |
| --------- | --------- |
| 🔥 80-100 | Excellent |
| ✅ 65-79  | Good      |
| 😐 50-64  | Average   |
| ⚠️ 35-49  | Poor      |
| ❌ 0-34   | Very Poor |

**Scoring:** Goals +15 · Assists +8 · Rating ×7 · Minutes penalty · Yellow -10 · Red -30

---

## 📁 Project Structure

```
football-intelligence/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── services/
│       ├── football_data.py      Live 2025-26 data
│       ├── football_api.py       Historical backup
│       ├── fbref_scraper.py      Scraping fallback
│       ├── xg_calculator.py      ML predictions
│       ├── player_form.py        Form scoring
│       └── ai_reporter.py        Groq AI reports
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       └── styles/globals.css
├── database/
│   └── init.sql
└── n8n-workflows/
    └── football_pipeline.json
```

---

## 🗺️ Roadmap

### ✅ v1.0 — Current (Sept 2026)

- [x] Live standings — 6 leagues
- [x] Fixtures & top scorers
- [x] xG model (ROC-AUC 0.81)
- [x] AI reports (Groq LLaMA 3.3)
- [x] Smart Redis cache
- [x] Docker full stack
- [x] n8n automation

### 🔜 v1.1 — Oct 2026

- [ ] xG charts on fixture cards
- [ ] Player form on previews
- [ ] H2H visualization
- [ ] Mobile responsive

### 🔮 v2.0 — Q1 2027

- [ ] Injury tracker
- [ ] Lineup predictor (ML)
- [ ] WhatsApp bot
- [ ] PDF scouting exports
- [ ] Prediction accuracy tracking

---

## 🔧 Commands

```bash
docker-compose up -d                    # Start
docker-compose down                     # Stop
docker-compose logs -f backend          # Logs
docker-compose build --no-cache backend # Rebuild
docker-compose ps                       # Status
```

```bash
# Flush cache (force refresh)
docker exec fip-redis redis-cli -a redis2026secure FLUSHDB
```

---

## 🤝 Contributing

Contributions welcome! Fork → branch → commit → PR.

**Ideas:** more leagues (MLS, Brasileirao), tracking-data xG, pitch visualizations (mplsoccer), React Native app.

---

## 📄 License

MIT — free for learning and portfolio use.

---

## 👤 Author

**Ossamix-Dev** — \_Data Analyst

[![GitHub](https://img.shields.io/badge/GitHub-midasoda--arch-181717?style=flat-square&logo=github)](https://github.com/midasoda-arch)

---

<div align="center">

_"Bringing data science to the beautiful game"_

**⭐ Star this repo if it helped you!**

</div>
