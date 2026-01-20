{{ config( materialized='table' ) }}

with
    raw_data as (
        select cast(t.date_day as date) as date_day
        from generate_series(
                '2020-01-01'::date, '2027-12-31'::date, '1 day'::interval
            ) as t (date_day)
    )

select * from raw_data