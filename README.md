# 🏎️ Pit to Grid

An F1 race strategy analyzer and prediction platform. Pulls historical race and qualifying data (2021–2026) from [FastF1](https://github.com/theOehrly/Fast-F1), stores it in Postgres via Supabase, and serves it through a Django REST API — built toward a React frontend for strategy analysis, driver comparisons, and race outcome predictions.

> Not affiliated with Formula 1, FIA, or Liberty Media. Built for educational/portfolio purposes using publicly available data.

---

## Stack

| Layer | Tech |
|---|---|
| Data source | FastF1 |
| Backend | Django + Django REST Framework |
| Database | PostgreSQL (Supabase) |
| Frontend | React *(planned)* |
| ML | scikit-learn, trained via Google Colab *(planned)* |
| Deployment | Vercel (frontend) + Railway (backend) *(planned)* |

## Architecture

\`\`\`
FastF1 → ETL (Django management commands) → Supabase (Postgres)
                                                    │
                                          Django + DRF (JSON API)
                                                    │
                                              React (planned)
\`\`\`

## Repo structure

\`\`\`
backend/     Django + DRF API, ETL scripts, models
frontend/    React app (planned)
ml/          Notebooks, training scripts, trained models
\`\`\`
---

## Progress Log

| Commit | Description |
|---|---|
| `Initial backend` | Models, admin, FastF1 sync command, local SQLite working |
| `update` | New season sync from API file and syncing data of races |
| `update` | `sync_season` command, fixed round-number matching bug, synced 2021–2022 |
| `fix` | `DataNotLoadedError` on partial weather data loads |
| `fix` | Driver mid-season team-swap DB constraint bug, slowed sync to respect rate limit |
| `add` | DRF API: serializers, views, and URLs for races/laps/pitstops/results |
| `add` | Initialize README with project details and setup instructions |
| `security` | Remove real-looking fallback SECRET_KEY, use obvious placeholder |
| `merge` | Merge remote README with local security fix |
| `update` | commit logs in README |
| `update` | formattings in README |


## Status

- [x] Repo scaffolded (monorepo: backend / frontend / ml)
- [x] Django models (Season, Team, Driver, DriverSeasonEntry, Race, Session, Lap, PitStop, Result)
- [x] ETL pipeline (FastF1 → Supabase), idempotent via `update_or_create`
- [x] 2021–2026 seasons synced and verified (129 races, race + qualifying)
- [x] DRF API — tested live against real Supabase data
- [ ] React frontend
- [ ] ML models (lap prediction, winner prediction, tire wear, pit strategy)
- [ ] Prediction game + user authentication

## Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # fill in DATABASE_URL (Supabase Session Pooler)
python manage.py migrate
python manage.py runserver
```

## Syncing race data

```bash
# One session
python manage.py sync_race_data --year 2023 --race 6 --session R

# Full season (race + qualifying, all rounds)
python manage.py sync_season --year 2023
```

Both commands are safe to re-run — they update existing rows rather than duplicating them.

## API endpoints

\`\`\`
GET /api/races/?season=2023
GET /api/races/<race_id>/laps/?session=R
GET /api/races/<race_id>/pitstops/?session=R
GET /api/races/<race_id>/results/?session=Q
\`\`\`