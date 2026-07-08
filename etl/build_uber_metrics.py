import os

from sqlalchemy import create_engine, text


DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "warehouse")
DB_USER = os.getenv("POSTGRES_USER", "etl")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "etl")
MILE_COST = float(os.getenv("MILE_COST", "0.35"))


def main() -> None:
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    sql = f"""
    create schema if not exists analytics;

    drop view if exists analytics.daily_earnings;
    create view analytics.daily_earnings as
    with trip_base as (
        select
            t.trip_date as metric_date,
            t.neighborhood,
            t.trip_earnings,
            coalesce(tp.tip_amount, 0) as tip_amount
        from raw.trips t
        left join raw.tips tp on tp.trip_id = t.trip_id
    ),
    bonus_base as (
        select
            b.bonus_date as metric_date,
            b.neighborhood,
            sum(b.bonus_amount) as bonus_amount
        from raw.bonuses b
        group by 1, 2
    ),
    hours_base as (
        select
            h.shift_date as metric_date,
            h.neighborhood,
            sum(h.hours_worked) as hours_worked
        from raw.hours h
        group by 1, 2
    ),
    gas_base as (
        select
            g.expense_date as metric_date,
            g.neighborhood,
            sum(g.gas_cost) as gas_cost
        from raw.gas g
        group by 1, 2
    ),
    mileage_base as (
        select
            m.mileage_date as metric_date,
            m.neighborhood,
            sum(m.miles_driven) as miles_driven
        from raw.mileage m
        group by 1, 2
    ),
    trip_rollup as (
        select
            metric_date,
            neighborhood,
            sum(trip_earnings) as trip_earnings,
            sum(tip_amount) as tips,
            count(*) as trips
        from trip_base
        group by 1, 2
    )
    select
        t.metric_date,
        t.neighborhood,
        t.trips,
        t.trip_earnings,
        t.tips,
        coalesce(b.bonus_amount, 0) as bonuses,
        coalesce(h.hours_worked, 0) as hours_worked,
        coalesce(g.gas_cost, 0) as gas_cost,
        coalesce(m.miles_driven, 0) as miles_driven,
        (coalesce(m.miles_driven, 0) * {MILE_COST})::numeric(12,2) as mileage_cost,
        (t.trip_earnings + t.tips + coalesce(b.bonus_amount, 0))::numeric(12,2) as gross_earnings,
        (coalesce(g.gas_cost, 0) + coalesce(m.miles_driven, 0) * {MILE_COST})::numeric(12,2) as total_expenses,
        (
            t.trip_earnings
            + t.tips
            + coalesce(b.bonus_amount, 0)
            - coalesce(g.gas_cost, 0)
            - coalesce(m.miles_driven, 0) * {MILE_COST}
        )::numeric(12,2) as profit_after_expenses,
        case
            when coalesce(h.hours_worked, 0) = 0 then 0
            else round(
                (
                    t.trip_earnings
                    + t.tips
                    + coalesce(b.bonus_amount, 0)
                    - coalesce(g.gas_cost, 0)
                    - coalesce(m.miles_driven, 0) * {MILE_COST}
                ) / h.hours_worked,
                2
            )
        end as hourly_rate
    from trip_rollup t
    left join bonus_base b on b.metric_date = t.metric_date and b.neighborhood = t.neighborhood
    left join hours_base h on h.metric_date = t.metric_date and h.neighborhood = t.neighborhood
    left join gas_base g on g.metric_date = t.metric_date and g.neighborhood = t.neighborhood
    left join mileage_base m on m.metric_date = t.metric_date and m.neighborhood = t.neighborhood
    order by t.metric_date, t.neighborhood;

    drop view if exists analytics.weekly_earnings;
    create view analytics.weekly_earnings as
    select
        date_trunc('week', metric_date)::date as week_start,
        sum(gross_earnings)::numeric(12,2) as weekly_gross_earnings,
        sum(total_expenses)::numeric(12,2) as weekly_expenses,
        sum(profit_after_expenses)::numeric(12,2) as weekly_profit_after_expenses,
        round(avg(hourly_rate), 2) as avg_hourly_rate
    from analytics.daily_earnings
    group by 1
    order by 1;

    drop view if exists analytics.best_neighborhoods;
    create view analytics.best_neighborhoods as
    select
        neighborhood,
        sum(gross_earnings)::numeric(12,2) as gross_earnings,
        sum(total_expenses)::numeric(12,2) as total_expenses,
        sum(profit_after_expenses)::numeric(12,2) as profit_after_expenses,
        round(avg(hourly_rate), 2) as avg_hourly_rate,
        rank() over (order by sum(profit_after_expenses) desc) as neighborhood_rank
    from analytics.daily_earnings
    group by neighborhood
    order by neighborhood_rank;

    drop view if exists analytics.dashboard_kpis;
    create view analytics.dashboard_kpis as
    select 'hourly_rate'::text as metric, round(avg(hourly_rate), 2)::numeric(12,2) as value
    from analytics.daily_earnings
    union all
    select 'daily_earnings'::text as metric, round(avg(gross_earnings), 2)::numeric(12,2) as value
    from analytics.daily_earnings
    union all
    select 'weekly_earnings'::text as metric, coalesce((select weekly_gross_earnings from analytics.weekly_earnings order by week_start desc limit 1), 0)::numeric(12,2) as value
    union all
    select 'profit_after_expenses'::text as metric, round(sum(profit_after_expenses), 2)::numeric(12,2) as value
    from analytics.daily_earnings;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Built analytics views: daily_earnings, weekly_earnings, best_neighborhoods, dashboard_kpis")


if __name__ == "__main__":
    main()
