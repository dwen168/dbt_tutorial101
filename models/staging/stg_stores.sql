
WITH

source as (
    select * from {{ source('raw', 'raw_stores') }}
),

renamed as (
    select
        id as store_id,
        name as store_location,
        tax_rate as location_tax_rate,
        {{ dbt.date_trunc('day', 'opened_at') }} as store_opened_date
    from source
)
select * from renamed