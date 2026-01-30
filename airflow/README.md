# Airflow + dbt Setup Guide

## Architecture Overview

### Two PostgreSQL Instances
1. **Data Warehouse Postgres** (macOS host)
   - Port: `5432`
   - Location: Running on your macOS
   - Purpose: Stores your data (raw, staging, marts)
   - Used by: dbt transformations

2. **Airflow Metadata Postgres** (Docker container)
   - Port: `5433` (exposed to host)
   - Location: Running inside Docker
   - Purpose: Stores Airflow metadata (DAG runs, tasks, connections)
   - Used by: Airflow services

## dbt Profile Targets

### `dev` Target (Local Development)
```bash
dbt run --target dev
dbt test --target dev
```
- Uses: `localhost:5432`
- For: Running dbt commands directly from your macOS terminal
- When: Developing and testing dbt models locally

### `docker` Target (Airflow Execution)
```bash
dbt run --target docker
dbt test --target docker
```
- Uses: `host.docker.internal:5432`
- For: Running dbt from inside Airflow containers
- When: DAGs execute dbt commands

## Usage

### Building and Starting Airflow
```bash
cd /Users/don168/mycode/dbt-tutorial101/airflow

# Build custom image with dbt
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Accessing Services
- **Airflow UI**: http://localhost:8080
  - Username: `airflow`
  - Password: `airflow`
- **Airflow Metadata DB** (if needed): `localhost:5433`

### dbt Project Location in Docker
- **Path inside containers**: `/opt/dbt`
- **Your DAGs can run**:
  ```bash
  cd /opt/dbt && dbt run --target docker
  ```

## Directory Structure
```
dbt-tutorial101/
├── airflow/
│   ├── docker-compose.yaml
│   ├── Dockerfile
│   ├── dags/              # Your Airflow DAGs go here
│   ├── logs/              # Airflow logs
│   ├── config/            # Airflow config files
│   └── plugins/           # Airflow plugins
├── models/                # dbt models
├── seeds/                 # dbt seed data
├── profiles.yml           # dbt connection profiles
└── dbt_project.yml        # dbt project config
```

## Important Notes

1. **Always specify `--target docker`** in your Airflow DAGs when running dbt commands
2. The default target is `dev` for local development
3. Both targets connect to the same database but use different host resolution
4. Your dbt project is mounted as a volume, so changes are immediately visible to Airflow
