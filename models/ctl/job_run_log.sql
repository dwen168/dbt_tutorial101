{{ config( materialized='table', schema='ctl' ) }}

-- Table structure for automated job logging
select
    cast(null as varchar(255)) as job_run_id,
    cast(null as timestamp) as run_started_at,
    cast(null as timestamp) as run_completed_at,
    cast(null as varchar(255)) as job_name,
    cast(null as varchar(50)) as job_type,
    cast(null as varchar(20)) as status,
    cast(null as text) as error_message,
    cast(null as text) as adapter_response,
    cast(null as bigint) as rows_affected,
    cast(null as bigint) as target_rows,
    cast(null as numeric) as run_duration_seconds,
    cast(null as varchar(50)) as invocation_id,
    cast(null as varchar(50)) as target_name,
    cast(null as varchar(255)) as destination_table,
    cast(null as varchar(50)) as materialization_type,
    cast(null as boolean) as is_full_refresh,
    cast(null as varchar(500)) as source_file_path
where
    1 = 0