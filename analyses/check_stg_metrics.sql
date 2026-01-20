select job_name, load_strategy, incremental_output, total_output 
from {{ ref('job_run_history') }} 
where job_name = 'stg_customer' 
order by run_started_at_local desc