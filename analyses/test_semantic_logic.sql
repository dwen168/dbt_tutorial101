-- Mock Semantic Layer Query
-- This tests the logic defined in your semantic_models

WITH daily_metrics as (
    select
        date_trunc('day', ordered_at) as metric_date,
        sum(order_total) as total_revenue,
        count(distinct order_id) as total_orders
    from {{ ref('fact_orders') }}
    group by 1
),

time_spine_check as (
    select
        ts.date_day,
        m.total_revenue,
        m.total_orders
    from {{ ref('time_spine') }} ts
    left join daily_metrics m on ts.date_day = m.metric_date
    where ts.date_day between '2024-09-01' and '2024-09-05'
)

select * from time_spine_check order by date_day