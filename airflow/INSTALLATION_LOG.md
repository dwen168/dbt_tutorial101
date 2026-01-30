# Airflow + dbt Installation Log

**Installation Date**: 2026-01-30  
**Status**: ✅ Successfully Completed

---

## 🎉 Installation Summary

Your Airflow + dbt environment is now **fully operational**!

### 🐳 Docker Containers Running

| Service | Status | Purpose |
|---------|--------|---------|
| **airflow-apiserver** | ✅ Healthy | Airflow web UI & API |
| **airflow-scheduler** | ✅ Healthy | DAG scheduling |
| **airflow-worker** | ✅ Healthy | Task execution (with dbt!) |
| **airflow-dag-processor** | ✅ Healthy | DAG parsing |
| **airflow-triggerer** | ✅ Healthy | Deferred tasks |
| **postgres** | ✅ Healthy | Airflow metadata (port 5433) |
| **redis** | ✅ Healthy | Celery message broker |

### 📦 Installed Packages

- ✅ **dbt-core**: 1.11.2
- ✅ **dbt-postgres**: 1.10.0
- ✅ **astronomer-cosmos**: Latest (for dbt integration in Airflow)

### 🔗 Connections Verified

- ✅ dbt can connect to your **macOS PostgreSQL** (port 5432) via `host.docker.internal`
- ✅ dbt project mounted at `/opt/dbt` in all containers
- ✅ profiles.yml configured with both `dev` and `docker` targets

### 🌐 Access Points

- **Airflow UI**: http://localhost:8080
  - Username: `airflow`
  - Password: `airflow`
- **Airflow Metadata DB**: `localhost:5433`
  - User: `airflow`
  - Password: `airflow`
  - Database: `airflow`
- **Your Data Warehouse**: `localhost:5432`
  - User: `postgres`
  - Password: `mysecretpassword`
  - Database: `postgres`

---

## 📋 Architecture Overview

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

### dbt Profile Targets

#### `dev` Target (Local Development)
- Host: `localhost`
- Port: `5432`
- Use for: Running dbt commands directly from your macOS terminal
- Example: `dbt run`, `dbt test`, `dbt seed`

#### `docker` Target (Airflow Execution)
- Host: `host.docker.internal`
- Port: `5432`
- Use for: Running dbt from inside Airflow containers
- Example: `dbt run --target docker`

---

## 🧪 Connection Test Results

```bash
$ docker-compose exec airflow-worker bash -c "cd /opt/dbt && dbt debug --target docker"

✅ Running with dbt=1.11.2
✅ profiles.yml file [OK found and valid]
✅ dbt_project.yml file [OK found and valid]
✅ Connection test: [OK connection ok]
✅ All checks passed!
```

---

## 🚀 Quick Start Commands

### Start Airflow
```bash
cd /Users/don168/mycode/dbt-tutorial101/airflow
docker-compose up -d
```

### Stop Airflow
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Rebuild Images (after Dockerfile changes)
```bash
docker-compose build
docker-compose up -d
```

### Run dbt Commands in Container
```bash
# Test connection
docker-compose exec airflow-worker bash -c "cd /opt/dbt && dbt debug --target docker"

# Run dbt models
docker-compose exec airflow-worker bash -c "cd /opt/dbt && dbt run --target docker"

# Run dbt tests
docker-compose exec airflow-worker bash -c "cd /opt/dbt && dbt test --target docker"
```

---

## 📂 Directory Structure

```
dbt-tutorial101/
├── airflow/
│   ├── docker-compose.yaml    # Docker services configuration
│   ├── Dockerfile             # Custom Airflow image with dbt
│   ├── dags/                  # Your Airflow DAGs go here
│   ├── logs/                  # Airflow logs
│   ├── config/                # Airflow config files
│   ├── plugins/               # Airflow plugins
│   ├── README.md              # Setup documentation
│   └── INSTALLATION_LOG.md    # This file
├── models/                    # dbt models
├── seeds/                     # dbt seed data
├── profiles.yml               # dbt connection profiles
└── dbt_project.yml            # dbt project config
```

---

## 📝 Next Steps

1. **Access Airflow UI**: Open http://localhost:8080 in your browser
2. **Create DAGs**: Add your Airflow DAG files to `airflow/dags/`
3. **Use Astronomer Cosmos**: Leverage Cosmos to orchestrate dbt models in Airflow
4. **Run dbt in DAGs**: Use `--target docker` when executing dbt commands from Airflow

### Example DAG with dbt
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'dbt_example',
    start_date=datetime(2026, 1, 30),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/dbt && dbt run --target docker'
    )
    
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/dbt && dbt test --target docker'
    )
    
    dbt_run >> dbt_test
```

---

## 🔧 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs airflow-worker

# Restart services
docker-compose restart
```

### dbt connection issues
```bash
# Verify profiles.yml is mounted
docker-compose exec airflow-worker cat /home/airflow/.dbt/profiles.yml

# Test connection
docker-compose exec airflow-worker bash -c "cd /opt/dbt && dbt debug --target docker"
```

### Port conflicts
- Airflow UI (8080): Change in docker-compose.yaml
- Airflow Postgres (5433): Change in docker-compose.yaml
- Your Postgres (5432): This should remain unchanged

---

## ✅ Installation Checklist

- [x] Docker images built successfully
- [x] All containers running and healthy
- [x] dbt-core and dbt-postgres installed
- [x] Astronomer Cosmos installed
- [x] dbt project mounted at /opt/dbt
- [x] profiles.yml configured with dev and docker targets
- [x] Connection to macOS PostgreSQL verified
- [x] dbt debug test passed
- [x] Airflow UI accessible at localhost:8080

---

---

## 🔐 Security Patch (Applied 2026-01-30)

**Issue**: Tasks failed with `ServerResponseError: Invalid auth token: Signature verification failed`.
**Cause**: Airflow 3.x requires a shared `SECRET_KEY` and `FERNET_KEY` between the API Server and Workers for JWT signing when using the Execution API. Without explicit configuration, services may generate random keys, leading to mismatch.

**Solution Applied**:
1.  Generated stable keys using `openssl`.
2.  Added keys to `airflow/.env`:
    *   `AIRFLOW__CORE__FERNET_KEY`
    *   `AIRFLOW__CORE__SECRET_KEY`
3.  Updated `docker-compose.yaml` to pass these keys to all services.

---

**Last updated: 2026-01-30 at 18:51 AEDT**
