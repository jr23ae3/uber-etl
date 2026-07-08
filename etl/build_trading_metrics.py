import os

from sqlalchemy import create_engine, text


DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "warehouse")
DB_USER = os.getenv("POSTGRES_USER", "etl")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "etl")


def main() -> None:
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    sql = """
    create schema if not exists analytics;

    drop view if exists analytics.price_features;
    create view analytics.price_features as
    with ordered as (
        select
            symbol,
            candle_time,
            close_price,
            avg(close_price) over (
                partition by symbol
                order by candle_time
                rows between 4 preceding and current row
            ) as ma_5,
            avg(close_price) over (
                partition by symbol
                order by candle_time
                rows between 19 preceding and current row
            ) as ma_20,
            lag(close_price) over (partition by symbol order by candle_time) as prev_close
        from raw.market_ohlcv
    )
    select
        symbol,
        candle_time,
        close_price,
        ma_5,
        ma_20,
        case
            when prev_close is null or prev_close = 0 then 0
            else ((close_price - prev_close) / prev_close) * 100
        end as return_pct,
        case
            when ma_5 > ma_20 then 1
            else 0
        end as long_signal
    from ordered;

    drop view if exists analytics.strategy_pnl;
    create view analytics.strategy_pnl as
    with base as (
        select
            symbol,
            candle_time,
            close_price,
            ma_5,
            ma_20,
            return_pct,
            long_signal,
            lag(close_price) over (partition by symbol order by candle_time) as prev_close,
            lag(long_signal) over (partition by symbol order by candle_time) as prev_signal
        from analytics.price_features
    ),
    pnl_rows as (
        select
            symbol,
            candle_time,
            close_price,
            ma_5,
            ma_20,
            return_pct,
            long_signal,
            coalesce(prev_signal, 0) as position,
            case
                when prev_close is null then 0
                else (close_price - prev_close) * coalesce(prev_signal, 0)
            end as pnl
        from base
    ),
    equity as (
        select
            symbol,
            candle_time,
            close_price,
            ma_5,
            ma_20,
            return_pct,
            position,
            pnl,
            sum(pnl) over (partition by symbol order by candle_time) as equity
        from pnl_rows
    )
    select
        symbol,
        candle_time,
        close_price,
        ma_5,
        ma_20,
        return_pct,
        position,
        pnl,
        equity,
        equity - max(equity) over (
            partition by symbol
            order by candle_time
            rows between unbounded preceding and current row
        ) as drawdown
    from equity;

    drop view if exists analytics.strategy_summary;
    create view analytics.strategy_summary as
    with stats as (
        select
            symbol,
            count(*) filter (where pnl <> 0) as trade_count,
            count(*) filter (where pnl > 0) as winning_trades,
            sum(pnl) as total_pnl,
            stddev_samp(pnl) as pnl_risk,
            min(drawdown) as max_drawdown
        from analytics.strategy_pnl
        group by symbol
    ),
    latest_ma as (
        select distinct on (symbol)
            symbol,
            ma_5,
            ma_20
        from analytics.strategy_pnl
        order by symbol, candle_time desc
    )
    select
        s.symbol,
        s.trade_count,
        s.winning_trades,
        case
            when s.trade_count = 0 then 0
            else round((s.winning_trades::numeric / s.trade_count::numeric) * 100, 2)
        end as win_rate_pct,
        round(coalesce(s.total_pnl, 0)::numeric, 6) as total_pnl,
        round(coalesce(s.pnl_risk, 0)::numeric, 6) as risk_stddev,
        round(coalesce(s.max_drawdown, 0)::numeric, 6) as max_drawdown,
        round(coalesce(m.ma_5, 0)::numeric, 6) as latest_ma_5,
        round(coalesce(m.ma_20, 0)::numeric, 6) as latest_ma_20
    from stats s
    left join latest_ma m on m.symbol = s.symbol;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Built analytics views: price_features, strategy_pnl, strategy_summary")


if __name__ == "__main__":
    main()
