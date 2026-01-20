#!/usr/bin/env python3
"""
Script to log dbt job runs to the control table.
This can be used in orchestration tools like Airflow, Prefect, etc.
"""

import psycopg2
from datetime import datetime
import uuid

def log_job_run(
    job_name: str,
    status: str,
    invocation_id: str = None,
    error_message: str = None,
    run_duration: float = None,
    db_config: dict = None
):
    """
    Log a job run to the ctl.job_run_log table
    
    Args:
        job_name: Name of the dbt job/model
        status: 'success', 'failure', or 'running'
        invocation_id: Unique ID for this run (auto-generated if not provided)
        error_message: Error details if status is 'failure'
        run_duration: Duration in seconds
        db_config: Database connection config
    """
    
    if db_config is None:
        db_config = {
            'host': 'localhost',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'mysecretpassword',
            'port': 5432
        }
    
    if invocation_id is None:
        invocation_id = str(uuid.uuid4())
    
    job_run_id = f"{invocation_id}_{job_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    try:
        insert_query = """
            INSERT INTO ctl.job_run_log (
                job_run_id,
                run_started_at,
                run_completed_at,
                job_name,
                job_type,
                status,
                error_message,
                run_duration_seconds,
                invocation_id,
                target_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cur.execute(insert_query, (
            job_run_id,
            datetime.now(),
            datetime.now(),
            job_name,
            'dbt_model',
            status,
            error_message,
            run_duration,
            invocation_id,
            'dev'
        ))
        
        conn.commit()
        print(f"✅ Logged job run: {job_name} - {status}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error logging job run: {e}")
        raise
    
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    # Example usage
    
    # Log a successful run
    log_job_run(
        job_name='stg_customer',
        status='success',
        run_duration=2.5
    )
    
    # Log a failed run
    log_job_run(
        job_name='stg_orders',
        status='failure',
        error_message='Table raw.orders does not exist',
        run_duration=1.2
    )
