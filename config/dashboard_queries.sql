-- KPI summary
select *
from analytics.strategy_summary;

-- Equity and drawdown over time
select
    candle_time,
    equity,
    drawdown
from analytics.strategy_pnl
order by candle_time;

-- Moving averages and price trend
select
    candle_time,
    close_price,
    ma_5,
    ma_20
from analytics.price_features
order by candle_time;
