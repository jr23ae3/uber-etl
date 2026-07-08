import json
import os
from pathlib import Path
from typing import List

import pandas as pd
import requests
from sqlalchemy import create_engine, text


MARKET_API_URL = os.getenv("MARKET_API_URL", "https://api.binance.com/api/v3/klines")
SYMBOL = os.getenv("MARKET_SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("MARKET_INTERVAL", "1h")
LIMIT = int(os.getenv("MARKET_LIMIT", "300"))
USE_KAFKA = os.getenv("USE_KAFKA", "false").lower() == "true"
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "market-candles")

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "warehouse")
DB_USER = os.getenv("POSTGRES_USER", "etl")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "etl")

SAMPLE_OUT = Path(os.getenv("SAMPLE_OUT", "/workspace/data/sample/market_prices.csv"))


def fetch_market_candles() -> pd.DataFrame:
    response = requests.get(
        MARKET_API_URL,
        params={"symbol": SYMBOL, "interval": INTERVAL, "limit": LIMIT},
        timeout=30,
    )
    response.raise_for_status()

    rows: List[List[str]] = response.json()
    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
            "close_time",
            "quote_asset_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    out = pd.DataFrame(
        {
            "symbol": SYMBOL,
            "candle_time": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "open_price": pd.to_numeric(df["open_price"]),
            "high_price": pd.to_numeric(df["high_price"]),
            "low_price": pd.to_numeric(df["low_price"]),
            "close_price": pd.to_numeric(df["close_price"]),
            "volume": pd.to_numeric(df["volume"]),
            "source": "market_api",
        }
    )
    return out


def maybe_publish_kafka(df: pd.DataFrame) -> None:
    if not USE_KAFKA:
        return

    from kafka import KafkaProducer

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    for row in df.to_dict(orient="records"):
        payload = {**row, "candle_time": row["candle_time"].isoformat()}
        producer.send(KAFKA_TOPIC, payload)
    producer.flush()
    print(f"Published {len(df)} events to Kafka topic {KAFKA_TOPIC}")


def load_postgres(df: pd.DataFrame) -> None:
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    with engine.begin() as conn:
        conn.execute(text("delete from raw.market_ohlcv where symbol = :symbol"), {"symbol": SYMBOL})

    df.to_sql("market_ohlcv", con=engine, schema="raw", if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into raw.market_ohlcv for {SYMBOL}")


def write_sample(df: pd.DataFrame) -> None:
    SAMPLE_OUT.parent.mkdir(parents=True, exist_ok=True)
    sample_df = df.copy()
    sample_df["candle_time"] = sample_df["candle_time"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    sample_df.to_csv(SAMPLE_OUT, index=False)


def main() -> None:
    df = fetch_market_candles()
    write_sample(df)
    maybe_publish_kafka(df)
    load_postgres(df)


if __name__ == "__main__":
    main()
