-- Hourly rate (overall and by neighborhood)
select metric_date, neighborhood, hourly_rate
from analytics.daily_earnings
order by metric_date, neighborhood;

-- Daily earnings
select metric_date, sum(gross_earnings) as total_daily_earnings
from analytics.daily_earnings
group by metric_date
order by metric_date;

-- Weekly earnings
select *
from analytics.weekly_earnings
order by week_start;

-- Best neighborhoods
select *
from analytics.best_neighborhoods
order by neighborhood_rank;

-- Profit after expenses
select metric_date, sum(profit_after_expenses) as total_profit_after_expenses
from analytics.daily_earnings
group by metric_date
order by metric_date;
