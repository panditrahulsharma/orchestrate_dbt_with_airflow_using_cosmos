"""
Dynamic Cosmos DAG Generator from YAML Data Contracts
This script reads a data_contracts.yaml file and dynamically generates Cosmos DbtDAGs for backfilling.
"""

import os
from datetime import datetime
from pathlib import Path

import yaml
from cosmos import DbtDag, ProjectConfig, ProfileConfig, RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping

# Configuration paths
DAG_FOLDER = Path(__file__).parent
CONFIG_FILE = DAG_FOLDER / "config" / "data_contracts.yaml"
DBT_ROOT_PATH = "/opt/airflow/dags/include/jaffle_shop"

# Airflow profile configuration (shared across all DAGs)
profile_config = ProfileConfig(
    profile_name="jaffle_shop",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="postgres_conn",
        profile_args={"schema": "public"},
    ),
)

# Load data contracts from YAML
def load_data_contracts():
    """Load data contracts from YAML file."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Data contract file not found: {CONFIG_FILE}")
    
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f) or {}


# Generate DAGs dynamically
data_contracts = load_data_contracts()

for dag_id, config in data_contracts.items():
    # Extract configuration
    description = config.get("description", "dbt Cosmos DAG")
    owner = config.get("owner", "airflow")
    tags = config.get("tags", [])
    tags.append("cosmos")  # Add cosmos tag to all generated DAGs
    schedule = config.get("schedule", "@daily")
    models = config.get("models", [])
    
    # Extract model names for the select clause
    model_names = [model["name"] for model in models]
    
    # Create DbtDag for this data contract
    dag = DbtDag(
        # Cosmos-specific parameters
        project_config=ProjectConfig(
            dbt_project_path=DBT_ROOT_PATH,
        ),
        profile_config=profile_config,
        render_config=RenderConfig(
            select=model_names,  # Only run models specified in the contract
        ),
        operator_args={
            "install_deps": True,
            "full_refresh": True,  # For backfilling
        },
        # Standard Airflow DAG parameters
        dag_id=dag_id,
        description=description,
        schedule=schedule,
        start_date=datetime(2023, 1, 1),
        catchup=False,
        tags=tags,
        default_args={
            "retries": 2,
            "owner": owner,
        },
    )
    
    # Explicitly add the DAG to globals so Airflow discovers it
    globals()[dag_id] = dag
