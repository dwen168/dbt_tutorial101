from datetime import datetime
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

with DAG(
    dag_id="dbt_pipeline_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["dbt", "pipeline"]
) as dag:

    # 1. Trigger Ctl DAG
    trigger_ctl = TriggerDagRunOperator(
        task_id="trigger_ctl",
        trigger_dag_id="dbt_ctl_dag",
        wait_for_completion=True,
        poke_interval=30
    )

    # 2. Trigger Seed DAG
    trigger_seed = TriggerDagRunOperator(
        task_id="trigger_seed",
        trigger_dag_id="dbt_seed_dag",
        wait_for_completion=True,
        poke_interval=30
    )

    # 3. Trigger Staging DAG
    trigger_staging = TriggerDagRunOperator(
        task_id="trigger_staging",
        trigger_dag_id="dbt_staging_dag",
        wait_for_completion=True,
        poke_interval=30
    )

    # 4. Trigger Marts DAG
    trigger_marts = TriggerDagRunOperator(
        task_id="trigger_marts",
        trigger_dag_id="dbt_marts_dag",
        wait_for_completion=True,
        poke_interval=30
    )

    # Define the sequential order
    trigger_ctl >> trigger_seed >> trigger_staging >> trigger_marts
