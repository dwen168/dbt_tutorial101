from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'sub_dbt_ctl',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['component', 'dbt_internal'],
) as dag:

    run_ctl = BashOperator(
        task_id='dbt_run_ctl',
        bash_command='cd /opt/dbt && dbt run --select path:models/ctl --target docker',
    )
    test_ctl = BashOperator(
        task_id='dbt_test_ctl',
        bash_command='cd /opt/dbt && dbt test --select path:models/ctl --target docker',
    )
    run_ctl >> test_ctl
