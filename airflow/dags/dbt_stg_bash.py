from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'sub_dbt_stg',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['component', 'dbt_internal'],
) as dag:

    run_stg = BashOperator(
        task_id='dbt_run_stg',
        bash_command='cd /opt/dbt && dbt run --select path:models/staging --target docker',
    )
    test_stg = BashOperator(
        task_id='dbt_test_stg',
        bash_command='cd /opt/dbt && dbt test --select path:models/staging --target docker',
    )
    run_stg >> test_stg
