create schema if not exists raw;
create schema if not exists analytics;

create table if not exists raw.market_ohlcv (
    symbol text not null,
    candle_time timestamptz not null,
    open_price numeric(18,8) not null,
    high_price numeric(18,8) not null,
    low_price numeric(18,8) not null,
    close_price numeric(18,8) not null,
    volume numeric(22,8) not null,
    source text not null,
    loaded_at timestamptz not null default now(),
    primary key (symbol, candle_time)
);
