{{ config( materialized='view', schema='ctl' ) }}

-- Analytics view for job history with local time conversion
select
    job_run_id,
    run_started_at at time zone 'UTC' at time zone 'Australia/Sydney' as run_started_at_local,
    job_name,
    job_type,
    status,

-- Metrics
rows_affected as incremental_output,
    target_rows as total_output,

    case 
        when job_type = 'seed' then 'FULL LOAD (SEED)'
        when is_full_refresh = true then 'FULL REFRESH'
        when materialization_type = 'incremental' then 'INCREMENTAL LOAD'
        when materialization_type = 'table' then 'FULL LOAD (TABLE)'
        when materialization_type = 'view' then 'VIEW (VIRTUAL)'
        else upper(materialization_type)
    end as load_strategy,

    destination_table,
    adapter_response,
    error_message,
    run_duration_seconds as duration,
    invocation_id
from {{ ref('job_run_log') }}
where job_run_id is not null
order by run_started_at desc