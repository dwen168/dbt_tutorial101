
WITH

source as (
    select * from {{ source('raw', 'raw_supplies') }}
),

renamed as (
    select
        -- Surrogate key using MD5 to replace dbt_utils
        md5(coalesce(cast(id as varchar), '') || '-' || coalesce(cast(sku as varchar), '')) as supply_uuid,
        id as supply_id,
        sku as product_id,
        name as supply_name,

        {{ cents_to_dollars('cost') }} as supply_cost,
        perishable as is_perishable_supply
        
    from source
)

select * from renamed