# Uber Earnings Analytics

Pipeline:

Import CSVs -> Python -> Postgres -> Dashboard

## Imported Data
- Trips
- Tips
- Bonuses
- Hours
- Gas
- Mileage

## Dashboard Metrics
- Hourly rate
- Daily earnings
- Weekly earnings
- Best neighborhoods
- Profit after expenses

## Stack
- Python ETL: pandas + SQLAlchemy
- Warehouse: Postgres 16
- Dashboard: Metabase
- Local orchestration: Docker Compose

## Project Structure
```text
.
├── config/dashboard_queries.sql
├── data/sample/
│   ├── trips.csv
│   ├── tips.csv
│   ├── bonuses.csv
│   ├── hours.csv
│   ├── gas.csv
│   └── mileage.csv
├── docker-compose.yml
├── docs/architecture.md
├── etl/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── load_uber_data.py
│   └── build_uber_metrics.py
└── sql/init/001_init.sql
```

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/jr23ae3/uber-etl.git
   cd uber-etl
   ```

2. Start services:
   ```bash
   docker compose up -d postgres adminer metabase
   ```

3. Load imported Uber earnings data:
   ```bash
   docker compose run --rm python-etl
   ```

4. Build analytics views:
   ```bash
   docker compose run --rm python-etl python etl/build_uber_metrics.py
   ```

5. Open tools:
- Adminer: http://localhost:8080
- Metabase: http://localhost:3002

## Warehouse Objects
- Raw tables: `raw.trips`, `raw.tips`, `raw.bonuses`, `raw.hours`, `raw.gas`, `raw.mileage`
- Analytics views:
  - `analytics.daily_earnings`
  - `analytics.weekly_earnings`
  - `analytics.best_neighborhoods`
  - `analytics.dashboard_kpis`

## Notes
- `profit_after_expenses` subtracts gas and mileage costs from gross earnings.
- Mileage cost uses the configurable `MILE_COST` value (default `0.35` per mile).
