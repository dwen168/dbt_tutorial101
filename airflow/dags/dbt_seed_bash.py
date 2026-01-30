from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_platform',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    'sub_dbt_seed',
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=['component', 'dbt_internal'], # Use tags for UI filtering
) as dag:

    run_seed = BashOperator(
        task_id='dbt_seed',
        bash_command='cd /opt/dbt && dbt seed --target docker --vars "load_source_data: true"',
    )
    test_seed = BashOperator(
        task_id='dbt_test_seed',
        bash_command='cd /opt/dbt && dbt test --select resource_type:seed --target docker',
    )
    run_seed >> test_seed
