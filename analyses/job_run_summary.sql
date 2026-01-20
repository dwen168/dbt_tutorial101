-- Job run summary by job name
select 
    job_name,
    count(*) as total_runs,
    sum(case when status = 'success' then 1 else 0 end) as successful_runs,
    sum(case when status = 'failure' then 1 else 0 end) as failed_runs,
    round(avg(run_duration_seconds), 2) as avg_duration_sec,
    round(max(run_duration_seconds), 2) as max_duration_sec,
    max(run_started_at) as last_run_at
from {{ ref('job_run_log') }}
where job_run_id is not null
group by job_name
order by total_runs desc