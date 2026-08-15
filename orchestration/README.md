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

### Operational notes (learned debugging this)

- **Workers need every dependency the tasks call.** A task that shells out to
  `feast` fails with "command not found" on the stock Airflow image — the
  binary has to be installed in the *worker* image, not just on the host. Fixed
  with a custom image (`Dockerfile` extending `apache/airflow` + `pip install
  feast`). This is why real Airflow deployments bake pipeline dependencies into
  a custom image.

- **Multi-component Airflow must share a signing key.** The webserver couldn't
  fetch task logs from the scheduler (`403 Could not read served logs`) because
  each component generated its own random `secret_key`. Pinning
  `AIRFLOW__WEBSERVER__SECRET_KEY` across all components fixes log serving —
  a distributed-systems config detail that shows up operating Airflow for real.

- **Upstream failure cascades.** When `feast_apply` failed, the downstream tasks
  showed `upstream_failed` and never ran — the dependency graph correctly
  refusing to run steps whose prerequisites didn't succeed.
  
## Running

```bash
docker compose up -d          # start Airflow (webserver, scheduler, db)
# open http://localhost:8080  (default login airflow/airflow)
# trigger the ml_pipeline DAG from the UI, or:
docker compose run airflow-cli dags trigger ml_pipeline
docker compose down           # stop
```
