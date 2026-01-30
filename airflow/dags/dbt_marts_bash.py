from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'sub_dbt_marts',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['component', 'dbt_internal'],
) as dag:

    run_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command='cd /opt/dbt && dbt run --select path:models/marts --target docker',
    )
    test_marts = BashOperator(
        task_id='dbt_test_marts',
        bash_command='cd /opt/dbt && dbt test --select path:models/marts --target docker',
    )
    run_marts >> test_marts
