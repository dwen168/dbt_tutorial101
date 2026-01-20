{{ config( materialized='table', schema='ctl' ) }}

-- Create / Widened table structure for job run logging
select
    cast(null as varchar(255)) as job_run_id,
    cast(null as timestamp) as run_started_at,
    cast(null as timestamp) as run_completed_at,
    cast(null as varchar(255)) as job_name,
    cast(null as varchar(50)) as job_type,
    cast(null as varchar(20)) as status,
    cast(null as text) as error_message,
    cast(null as numeric) as run_duration_seconds,
    cast(null as varchar(50)) as invocation_id,
    cast(null as varchar(50)) as target_name
where
    1 = 0