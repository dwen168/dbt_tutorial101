
with

source as (
    select * from {{ source('raw', 'raw_products') }}
),

renamed as (
    select
        sku as product_id,
        name as product_name,
        type as product_type,
        description as product_description,

        {{ cents_to_dollars('price')}} as product_price,
        case when type = 'jaffle' then true else false end as is_food_item,
        case when type = 'beverage' then true else false end as is_drink_item

    from source
)
select * from renamed