# Trading Data Pipeline

End-to-end trading analytics flow:

Market API -> Kafka (optional) -> Python -> Postgres -> Dashboard

## Metrics
- Win rate
- Risk
- P/L
- Drawdown
- Moving averages

## Stack
- Market API: Binance Klines REST API
- Optional stream layer: Kafka + Kafka UI (Docker profile `kafka`)
- ETL/metrics: Python (`requests`, `pandas`, `SQLAlchemy`)
- Warehouse: Postgres 16
- Dashboard: Metabase

## Repository Layout
```text
.
├── data/sample/market_prices.csv
├── docker-compose.yml
├── docs/architecture.md
├── etl/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── load_market_data.py
│   └── build_trading_metrics.py
├── screenshots/README.md
└── sql/init/001_init.sql
```

## Setup Instructions
1. Clone:
   ```bash
   git clone https://github.com/jr23ae3/uber-etl.git
   cd uber-etl
   ```

2. Start core services:
   ```bash
   docker compose up -d postgres adminer metabase
   ```

3. Run ETL load (Market API -> Postgres):
   ```bash
   docker compose run --rm python-etl
   ```

4. Build metric views:
   ```bash
   docker compose run --rm python-etl python etl/build_trading_metrics.py
   ```

5. Optional Kafka stack:
   ```bash
   docker compose --profile kafka up -d zookeeper kafka kafka-ui
   docker compose run --rm -e USE_KAFKA=true python-etl
   ```

6. Open tools:
- Adminer: http://localhost:8082
- Metabase: http://localhost:3002
- Kafka UI: http://localhost:8083 (optional)

## Postgres Objects
- Raw table: `raw.market_ohlcv`
- Analytics views:
  - `analytics.price_features` (includes MA5/MA20)
  - `analytics.strategy_pnl` (position P/L + drawdown curve)
  - `analytics.strategy_summary` (win rate, risk, P/L, drawdown, latest moving averages)

## Dashboard Starting Point
Use `analytics.strategy_summary` for headline KPIs and `analytics.strategy_pnl` for equity and drawdown charts.
