-- Query to view recent job runs
select 
    job_name,
    status,
    error_message,
    run_duration_seconds,
    to_char(run_started_at, 'YYYY-MM-DD HH24:MI:SS') as run_started_at,
    to_char(run_completed_at, 'YYYY-MM-DD HH24:MI:SS') as run_completed_at
from {{ ref('job_run_log') }}
where job_run_id is not null
order by run_started_at desc
limit 10