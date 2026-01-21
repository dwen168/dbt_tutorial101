FROM apache/airflow:2.10.4

# Use constraints file from the official Airflow repository
ARG AIRFLOW_VERSION=2.10.4
ARG PYTHON_VERSION=3.12
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

USER root
# Install build dependencies for psycopg2 and other packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# 1. Install dbt in a separate virtual environment to avoid conflicts with Airflow's constraints
RUN python -m venv /home/airflow/dbt_venv && \
    /home/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres

# 2. Install Cosmos and other providers in the main Airflow environment
RUN pip install --no-cache-dir \
    "astronomer-cosmos" \
    "apache-airflow-providers-fab" \
    --constraint "${CONSTRAINT_URL}"

# Create dbt project directory
USER root
RUN mkdir -p /opt/airflow/dbt_project && chown airflow: /opt/airflow/dbt_project
USER airflow

WORKDIR /opt/airflow

# Copy dbt project files
COPY --chown=airflow:airflow . /opt/airflow/dbt_project

# Set the dbt path in the DAG environment (we will use this in the DAG file)
ENV ASTRO_PYPI_DBT_EXECUTABLE=/home/airflow/dbt_venv/bin/dbt
