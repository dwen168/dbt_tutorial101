from datetime import datetime
import os
from pathlib import Path

from airflow import DAG
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from cosmos.operators import DbtSeedOperator
from cosmos.constants import InvocationMode, TestBehavior

# Path to your dbt project
DBT_PROJECT_PATH = Path("/opt/airflow/dbt_project")

# Define the profile configuration
profile_config = ProfileConfig(
    profile_name="dbt_101_profile",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="postgres_default",
        profile_args={
            "schema": "stg",
        },
    ),
)

# Use the symlinked dbt at /usr/local/bin/dbt and force subprocess mode
execution_config = ExecutionConfig(
    dbt_executable_path="/usr/local/bin/dbt", 
    invocation_mode=InvocationMode.SUBPROCESS,
)

project_config = ProjectConfig(
    dbt_project_path=DBT_PROJECT_PATH,
    dbt_vars={"load_source_data": True},
)

# This is the original monolithic DAG, kept for testing purposes.
# Renamed dag_id to avoid confusion with the split DAGs.
with DAG(
    dag_id="dbt_tutorial_dag_test",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    seed_step = DbtSeedOperator(
        task_id="dbt_seed",
        project_dir=DBT_PROJECT_PATH,
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        vars={"load_source_data": True}
    )

    # 1. Utility (ctl models like job_run_log)
    utility = DbtTaskGroup(
        group_id="dbt_utility",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=RenderConfig(
            select=["path:models/ctl"]
        )
    )

    # 2. Staging models
    staging = DbtTaskGroup(
        group_id="dbt_staging",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        operator_args={
            "vars": {"load_source_data": True}
        },
        render_config=RenderConfig(
            select=["path:models/staging"],
            test_behavior=TestBehavior.AFTER_EACH
        )
    )

    # 3. Marts models
    marts = DbtTaskGroup(
        group_id="dbt_marts",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        operator_args={
            "vars": {"load_source_data": True}
        },
        render_config=RenderConfig(
            select=["path:models/marts"],
            test_behavior=TestBehavior.AFTER_ALL
        )
    )

    utility >> seed_step >> staging >> marts
