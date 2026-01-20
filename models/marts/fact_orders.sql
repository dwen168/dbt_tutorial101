{{ config( materialized='table' ) }}

WITH orders as ( select * from {{ ref('stg_orders') }} ),

-- Aggregating item metrics from fact_order_items

order_items_summary as (
    select
        order_id,
        sum(supply_cost) as order_supply_cost,
        sum(product_price) as order_items_subtotal,
        count(order_item_id) as order_item_count,
        sum(case when is_food_item then 1 else 0 end) as food_item_count,
        sum(case when is_drink_item then 1 else 0 end) as drink_item_count
    from {{ ref('fact_order_items') }}
    group by 1
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.store_id,
        o.ordered_at,
        o.subtotal as order_subtotal_raw,
        o.tax_paid,
        o.order_total,

-- Aggregated items metrics
coalesce(s.order_supply_cost, 0) as order_supply_cost,
coalesce(s.order_items_subtotal, 0) as order_items_subtotal,
coalesce(s.order_item_count, 0) as order_item_count,
coalesce(s.food_item_count, 0) as food_item_count,
coalesce(s.drink_item_count, 0) as drink_item_count,

-- Auditing columns
current_timestamp as data_loaded_at,
        '{{ invocation_id }}' as job_id

    from orders o
    left join order_items_summary s on o.order_id = s.order_id
)

select * from final