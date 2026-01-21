# Airflow Orchestration for dbt 101

This directory contains the Airflow setup for orchestrating the dbt project using [Astronomer Cosmos](https://github.com/astronomer/astronomer-cosmos).

## DAG Structure

The main DAG `dbt_tutorial_dag` is structured to ensure a clean, observable data pipeline. It uses `DbtTaskGroup` to organize dbt models into logical execution steps.

**Pipeline Flow:**
`Seed` -> `Utility` -> `Staging` -> `Marts`

### logical Stages

1.  **Seed (`dbt_seed`)**:
    - Loads raw CSV data from `seeds/` into the `raw` schema.
    - Ensures source data is present before any transformations.

2.  **Utility (`dbt_utility`)**:
    - **Models**: `models/ctl` (e.g., `job_run_log`).
    - **Purpose**: Initializes system tables required for logging and auditing.
    - **Note**: This step does not depend on source data loading vars, ensuring logs are set up even if seed data doesn't change.

3.  **Staging (`dbt_staging`)**:
    - **Models**: `models/staging`.
    - **Purpose**: Cleans and standardizes raw data (Materialized as Views).
    - **Behavior**: Runs all staging models, then runs their tests. Parallelism is contained within this group.

4.  **Marts (`dbt_marts`)**:
    - **Models**: `models/marts`.
    - **Purpose**: Builds business-facing tables (Materialized as Tables/Incremental).
    - **Behavior**: Runs only after *all* staging models successfully complete.

## Running Locally

1.  **Prerequisites**: Docker Desktop installed.
2.  **Start Services**:
    ```bash
    cd airflow
    docker-compose up -d
    ```
3.  **Access UI**: Open [http://localhost:8080](http://localhost:8080) (User/Pass: `airflow`/`airflow`).
4.  **Trigger DAG**: Enable and trigger `dbt_tutorial_dag`.

## Configuration

- **Cosmos execution_config**: Using `InvocationMode.SUBPROCESS` to avoid dependency conflicts.
- **Test Behavior**: `TestBehavior.AFTER_ALL` is used within groups to prevent "relation does not exist" errors during test execution.
