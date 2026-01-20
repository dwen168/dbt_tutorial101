{{ config( materialized='view', schema='ctl' ) }}

-- View to analyze job run history with local time conversion (AEST/AEDT)
select
    job_run_id,
    run_started_at as run_started_at_utc,
    run_completed_at as run_completed_at_utc,

-- Convert to Australian Eastern Time
-- Using 'Australia/Sydney' automatically handles AEST and AEDT (Daylight Savings)
run_started_at at time zone 'UTC' at time zone 'Australia/Sydney' as run_started_at_local,
run_completed_at at time zone 'UTC' at time zone 'Australia/Sydney' as run_completed_at_local,
job_name,
job_type,
status,
error_message,
run_duration_seconds,
invocation_id,
target_name,

-- Calculate run date in local time
date (
    run_started_at at time zone 'UTC' at time zone 'Australia/Sydney'
) as run_date_local,

-- Flag for failures
case when status in ('failure', 'error', 'fail') then 1 else 0 end as is_failure,
    -- Flag for success
    case when status in ('success', 'pass') then 1 else 0 end as is_success
from {{ ref('job_run_log') }}
where job_run_id is not null
order by run_started_at desc