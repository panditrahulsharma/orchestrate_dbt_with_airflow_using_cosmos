"""
An example DAG that uses Cosmos to render a dbt project.
"""

import os
from datetime import datetime
from pathlib import Path

from cosmos import DbtDag, ProjectConfig, ProfileConfig,RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping

# DEFAULT_DBT_ROOT_PATH = Path(__file__).parent / "dbt"
DBT_ROOT_PATH = '/opt/airflow/dags/include/jaffle_shop'

profile_config = ProfileConfig(
    profile_name="jaffle_shop",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="postgres_conn",
        profile_args={"schema": "public"},
    ),
)

# [START local_example]
# exclude models
# include models
dbt_cosmos_model_dag = DbtDag(
    # dbt/cosmos-specific parameters
    project_config=ProjectConfig(
        DBT_ROOT_PATH ,
    ),
    profile_config=profile_config,
    operator_args={
        "install_deps": True,  # install any necessary dependencies before running any dbt command
        "full_refresh": True,  # used only in dbt commands that support this flag
    },
    render_config=RenderConfig(
        select=["+orders"],  # Includes specific model + core tagged models
        # exclude=["tag:deprecated"]             # Excludes deprecated models
    ),
    # normal dag parameters
    schedule="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['dbt'],
    dag_id="dbt_cosmos_model_dag",
    default_args={"retries": 2},
)
# [END local_example]