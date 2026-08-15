# registry — MLflow

The "which model is which, and is it safe to ship" layer. Closes the gap
between training a model (the Ray component) and versioning, tracking, and
promoting it to production.

## Two concepts, two roles

**Experiment tracking** — every training run logs its params (lr, epochs),
metrics (loss), and artifacts (the model file). Answers "which run/hyperparams
were best?" and gives lineage: every model traces to exactly how it was made.

**Model registry** — registered models get versions (v1, v2, ...) and move
through stages: None -> Staging -> Production -> Archived. Promotion is the
shipping gate: register, evaluate in Staging, promote to Production only when it
passes.

## The serving indirection

Serving loads `models:/conversion_model/Production` — by STAGE, not version.
Promote a new version and what serves changes with zero code change. The
registry is the indirection layer between "a model" and "the model in prod."

## The config-swap theme

`MLFLOW_TRACKING_URI` points at a local `./mlruns` dir now, or a remote tracking
server + S3 artifact store in production — same logging/registry code either way.
Same pattern as the feature store's online-store swap and Airflow's executor.

## Flow

```
train (Ray) -> log_run (track + register)  -> promote_latest (Staging->Production)
                                            -> load_production (serve by stage)
```

## Landscape

MLflow vs alternatives: Weights & Biases (richer tracking UI, SaaS),
Neptune, SageMaker Model Registry (cloud-locked). MLflow chosen for being
open-source, self-hostable, and the de-facto standard registry API.

## Running

```bash
pip install mlflow
python -m registry.run_demo      # train -> track -> register -> promote -> load
mlflow ui                        # browse runs & registry at http://localhost:5000
```
