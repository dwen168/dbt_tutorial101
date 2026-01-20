
WITH

source as (
    select * from {{ source('raw', 'raw_orders') }}
),

renamed as (
    select
        id as order_id,
        store_id as store_id,
        customer as customer_id,
        subtotal as subtotal_cents,
        tax_paid as tax_paid_cents,
        order_total as order_total_cents
    from source
),

final as (
    select
        order_id,
        store_id,
        customer_id,
        subtotal_cents,
        tax_paid_cents,
        order_total_cents,
        {{ cents_to_dollars('subtotal_cents') }} as subtotal,
        {{ cents_to_dollars('tax_paid_cents') }} as tax_paid,
        {{ cents_to_dollars('order_total_cents') }} as order_total
    from renamed
)

select * from final