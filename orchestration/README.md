# orchestration — Airflow

Orchestrates the ML pipeline as a DAG: the tasks are the real feature-store
workflow from the `feature_store/` component, run in dependency order on a
schedule, with retries and backfill support.

## Why Airflow

The "how do jobs run reliably" layer. A DAG expresses *task dependencies*
(this before that), Airflow handles *scheduling* (run daily), *retries*
(a flaky task gets N attempts with backoff before failing the run), and
*backfills* (re-run the DAG for past dates — e.g. materialize features for
historical days). This is what turns a pile of scripts into an operable pipeline.

## The DAG

```
feast_apply → feast_materialize → train → evaluate → register
```

Each task maps to a real step. `feast_apply` registers definitions,
`feast_materialize` syncs offline→online for the run's date, then train/eval/
register (stubbed here; wired to the Ray + MLflow components later).

## Concepts demonstrated

- **DAG / dependencies** — the `>>` operators define the directed acyclic graph
- **Retries + backoff** — `retries` and `retry_delay` on task defaults
- **Scheduling** — `schedule` on the DAG (daily)
- **Backfill** — `catchup=True` lets Airflow run past dates; `{{ ds }}` templating
  passes each run's date into materialize, so re-running history is correct
- **Idempotency** — tasks re-run safely; feast apply/materialize are idempotent

## Landscape

Airflow is the industry-standard general scheduler. Modern ML-native
alternatives: ZenML and Dagster (higher-level, ML-aware abstractions,
asset/artifact-centric). Airflow chosen here because it's the baseline
expectation and doesn't hide the scheduling mechanics.

## Running

```bash
docker compose up -d          # start Airflow (webserver, scheduler, db)
# open http://localhost:8080  (default login airflow/airflow)
# trigger the ml_pipeline DAG from the UI, or:
docker compose run airflow-cli dags trigger ml_pipeline
docker compose down           # stop
```
