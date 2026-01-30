from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

with DAG(
    '01_DBT_MAIN_ORCHESTRATOR',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['orchestration', 'production'],
    description='Professional Orchestrator with Optimized Performance',
) as dag:

    # Global configuration for high-frequency polling
    # Removed 'deferrable: True' to avoid potential triggerer communication issues in local env
    trigger_config = {
        "wait_for_completion": True,
        "poke_interval": 5,  # Check sub-DAG status every 5 seconds (default is 60s)
    }

    t1 = TriggerDagRunOperator(
        task_id='trigger_ctl',
        trigger_dag_id='sub_dbt_ctl',
        **trigger_config
    )

    t2 = TriggerDagRunOperator(
        task_id='trigger_seed',
        trigger_dag_id='sub_dbt_seed',
        **trigger_config
    )

    t3 = TriggerDagRunOperator(
        task_id='trigger_stg',
        trigger_dag_id='sub_dbt_stg',
        **trigger_config
    )

    t4 = TriggerDagRunOperator(
        task_id='trigger_marts',
        trigger_dag_id='sub_dbt_marts',
        **trigger_config
    )

    # Execution order: Control -> Seed -> Staging -> Marts
    t1 >> t2 >> t3 >> t4
