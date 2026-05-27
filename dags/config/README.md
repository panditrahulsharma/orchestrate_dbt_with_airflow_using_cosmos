# Dynamic Cosmos DAG Generator

This system allows you to define multiple dbt projects and models in a single YAML file and automatically generate Cosmos DAGs from those definitions.

## How It Works

1. **Data Contract YAML** (`config/data_contracts.yaml`):
   - Each root key becomes a DAG ID
   - Contains model definitions, owner, tags, and schedule configuration

2. **Dynamic Generator** (`cosmos_dynamic_dag_generator.py`):
   - Reads the YAML file
   - For each contract, creates a Cosmos `DbtDag` 
   - Registers DAGs with Airflow automatically

## Configuration Structure

```yaml
dag_name:
  description: "Human-readable description"
  owner: "team_name"
  tags: ["tag1", "tag2"]
  schedule: "0 2 * * *"  # Cron schedule (optional, defaults to @daily)
  models:
    - name: model1
    - name: model2
```

### Fields:
- **dag_name** (key): The Airflow DAG ID
- **description**: Displayed in the Airflow UI
- **owner**: Owner of the DAG (appears in Airflow UI)
- **tags**: Labels for organization (cosmos tag is auto-added)
- **schedule**: Cron expression or preset (defaults to @daily)
- **models**: List of dbt model names to include in this DAG

## File Structure

```
dags/
├── config/
│   └── data_contracts.yaml       # Your data contract definitions
├── cosmos_dynamic_dag_generator.py # The DAG generator (discovered by Airflow)
├── include/
│   └── jaffle_shop/              # Your dbt project
└── ...
```

## Adding a New DAG

Simply add a new entry to `config/data_contracts.yaml`:

```yaml
my_new_dag:
  description: "My new backfill DAG"
  owner: "my_team"
  tags: ["backfill", "important"]
  schedule: "0 4 * * *"
  models:
    - name: my_model_1
    - name: my_model_2
```

Airflow will automatically discover and register this DAG on the next scheduler refresh.

## Backfilling

All DAGs created by this generator include:
- `full_refresh: True` - Rebuilds all models from scratch
- `retries: 2` - Automatic retry on failure
- Proper dependency handling between models

For backfilling specific date ranges, trigger the DAG manually in Airflow UI with:
- **Logical date**: Your backfill start date
- **Number of runs**: How many days/runs to backfill

## Troubleshooting

If DAGs don't appear in Airflow:

1. **Check syntax**:
   ```bash
   python3 -m py_compile dags/cosmos_dynamic_dag_generator.py
   ```

2. **Validate YAML**:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('dags/config/data_contracts.yaml'))"
   ```

3. **Check logs**:
   ```bash
   docker compose logs scheduler  # If using Docker
   ```

4. **Restart Airflow**:
   ```bash
   docker compose restart scheduler webserver
   ```

## Example Use Cases

### Case 1: Staging Layer Backfill
```yaml
staging_backfill:
  description: "Backfill all staging models"
  owner: "data_engineering"
  tags: ["staging", "backfill"]
  schedule: "0 1 * * *"
  models:
    - name: stg_customers
    - name: stg_orders
```

### Case 2: Reporting Models
```yaml
reports_production:
  description: "Production reporting models"
  owner: "analytics"
  tags: ["reporting", "production"]
  schedule: "0 6 * * *"  # Run after staging completes
  models:
    - name: fct_orders
    - name: dim_customers
```

## Advanced Options

You can extend `cosmos_dynamic_dag_generator.py` to support additional options:

- `exclude_models`: Models to exclude from the run
- `selector`: Use dbt selectors instead of explicit model lists
- `max_active_runs`: Limit concurrent DAG runs
- `retry_delay`: Custom retry delay in minutes
- `sla`: Service level agreement (time limit per DAG run)

## Links & Resources

- [Cosmos Documentation](https://airflow.apache.org/docs/apache-airflow-providers-dbt/stable/cosmos.html)
- [dbt Selection Syntax](https://docs.getdbt.com/reference/node-selection/syntax)
- [Airflow DAG Configuration](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html)
- [Airflow Scheduling](https://airflow.apache.org/docs/apache-airflow/stable/concepts/scheduling.html)
