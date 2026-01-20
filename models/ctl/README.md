# ETL Job Run Logging System

This folder contains the control tables and utilities for tracking ETL job execution history.

## Components

### 1. `job_run_log` (Table)
Main table that stores metadata for every individual job/model execution:
- `job_run_id`: Unique identifier (Invocation ID + Job Name)
- `run_started_at`: Timestamp when the dbt run started
- `run_completed_at`: Timestamp when the specific job finished
- `job_name`: Name of the model or test
- `job_type`: Type of resource (`model`, `test`, `seed`, etc.)
- `status`: Execution status (`success`, `fail`, `pass`, `error`)
- `error_message`: Full error text if the job failed
- `run_duration_seconds`: Time taken to execute
- `invocation_id`: Unique ID for the entire dbt command execution
- `target_name`: Target environment (e.g., `dev`, `prod`)

### 2. `job_run_history` (View)
Analytics view with additional calculated fields for easier monitoring:
- `run_date`: Date of execution
- `is_failure`: Boolean flag (1 for fails, 0 for pass/success)
- `is_success`: Boolean flag (1 for success/pass, 0 for fails)

---

## 🚀 How it Works (Automatic vs Manual)

The logging system has two modes of operation: **Full Auto** (for dbt tasks) and **Manual/Script** (for external tasks).

### 1. Automatic Logging (Highly Recommended)
This is achieved using **Macros + Hooks**. Every time you run `dbt run` or `dbt test`, the results are automatically saved.

*   **Macro**: `log_run_results(results)` loops through the built-in dbt results object.
*   **Trigger**: Configured in `dbt_project.yml` under `on-run-end`. It fires automatically when any dbt command finishes.

**Setup in `dbt_project.yml`:**
```yaml
on-run-end:
  - "{{ log_run_results(results) }}"
```

### 2. Manual/Script Logging
Use these when you want to record events that happen *outside* of dbt models, such as database maintenance or Python processing scripts.

*   **Macro `log_job_run`**: Used for one-off manual entries.
*   **Python `log_job_run.py`**: Used by orchestration tools (Airflow, Prefect) to record script execution.

---

## Usage Examples

### Method 1: Python Script (For Orchestration)

```python
from scripts.log_job_run import log_job_run

# Log a successful external task
log_job_run(
    job_name='my_python_script',
    status='success',
    run_duration=15.4
)
```

### Method 2: dbt Macro (Manual Post-Hook)

```sql
-- In your model's config for a specific manual log
{{ config(
    post_hook=[
        "{{ log_job_run('special_event', 'success') }}"
    ]
) }}
```

### Method 3: SQL Direct Insert

```sql
INSERT INTO ctl.job_run_log (job_run_id, job_name, status, invocation_id, target_name)
VALUES ('manual_001', 'data_cleanup', 'success', 'manual', 'dev');
```

---

## Querying Job Logs

### View Last 10 Runs
```sql
SELECT * FROM ctl.job_run_history
ORDER BY run_started_at DESC
LIMIT 10;
```

### Find Current Failures
```sql
SELECT job_name, error_message, run_started_at
FROM ctl.job_run_history
WHERE status IN ('fail', 'error')
ORDER BY run_started_at DESC;
```

### Performance Summary
```sql
SELECT 
    job_name,
    COUNT(*) as total_runs,
    SUM(is_success) as successful_runs,
    ROUND(AVG(run_duration_seconds), 2) as avg_sec
FROM ctl.job_run_history
GROUP BY job_name
ORDER BY total_runs DESC;
```

## Maintenance

### Clear Old Logs (Keep Last 90 Days)
```sql
DELETE FROM ctl.job_run_log
WHERE run_started_at < CURRENT_DATE - INTERVAL '90 days';
```
