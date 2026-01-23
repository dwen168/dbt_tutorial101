from datetime import datetime
from pathlib import Path

from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
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

# 3. Staging DAG
dbt_staging_dag = DbtDag(
    dag_id="dbt_staging_dag",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    project_config=project_config,
    profile_config=profile_config,
    execution_config=execution_config,
    render_config=RenderConfig(
        select=["path:models/staging"],
        test_behavior=TestBehavior.AFTER_ALL
    )
)
