from airflow import DAG
from airflow.operators.bash import BashOperator
# from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime
default_args = {
'start_date': datetime(2022, 1, 1),
}

DBT_ROOT_PATH = '/opt/airflow/dags/include/jaffle_shop'


dag = DAG(
    'dbt_custom_dag',
    default_args=default_args,
    tags=['dbt', 'custom'],
    schedule='0 0 * * *',  # Run daily at midnight
)
task1 = BashOperator(
    task_id='stg_customers',
    bash_command=f'dbt build --project-dir "{DBT_ROOT_PATH}" --models stg_customers',
    dag=dag,
)
task2 = BashOperator(
    task_id='stg_orders',
    bash_command=f'dbt build --project-dir "{DBT_ROOT_PATH}" --models stg_orders',
    dag=dag,
)

task1 >> task2