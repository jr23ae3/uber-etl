create schema if not exists raw;
create schema if not exists analytics;

create table if not exists raw.trips (
    trip_id text primary key,
    trip_date date not null,
    neighborhood text not null,
    trip_count integer not null,
    trip_earnings numeric(12,2) not null,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.tips (
    trip_id text primary key references raw.trips(trip_id),
    tip_amount numeric(12,2) not null,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.bonuses (
    bonus_id text primary key,
    bonus_date date not null,
    neighborhood text not null,
    bonus_amount numeric(12,2) not null,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.hours (
    shift_id text primary key,
    shift_date date not null,
    neighborhood text not null,
    hours_worked numeric(6,2) not null,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.gas (
    expense_id text primary key,
    expense_date date not null,
    neighborhood text not null,
    gas_cost numeric(12,2) not null,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.mileage (
    mileage_id text primary key,
    mileage_date date not null,
    neighborhood text not null,
    miles_driven numeric(10,2) not null,
    loaded_at timestamptz not null default now()
);
