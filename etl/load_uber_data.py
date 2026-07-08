import os
from pathlib import Path
from typing import Dict

import pandas as pd
from sqlalchemy import create_engine, text


DATA_DIR = Path(os.getenv("DATA_DIR", "/workspace/data/sample"))

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "warehouse")
DB_USER = os.getenv("POSTGRES_USER", "etl")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "etl")


def _read_csv(name: str, date_cols: list[str]) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing CSV file: {path}")
    df = pd.read_csv(path)
    for col in date_cols:
        df[col] = pd.to_datetime(df[col]).dt.date
    return df


def main() -> None:
    datasets: Dict[str, pd.DataFrame] = {
        "trips": _read_csv("trips", ["trip_date"]),
        "tips": _read_csv("tips", []),
        "bonuses": _read_csv("bonuses", ["bonus_date"]),
        "hours": _read_csv("hours", ["shift_date"]),
        "gas": _read_csv("gas", ["expense_date"]),
        "mileage": _read_csv("mileage", ["mileage_date"]),
    }

    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    with engine.begin() as conn:
        conn.execute(text("truncate table raw.tips"))
        conn.execute(text("truncate table raw.trips"))
        conn.execute(text("truncate table raw.bonuses"))
        conn.execute(text("truncate table raw.hours"))
        conn.execute(text("truncate table raw.gas"))
        conn.execute(text("truncate table raw.mileage"))

    for table, df in datasets.items():
        df.to_sql(table, con=engine, schema="raw", if_exists="append", index=False)

    print(
        "Loaded rows => "
        + ", ".join([f"{table}={len(df)}" for table, df in datasets.items()])
    )


if __name__ == "__main__":
    main()
