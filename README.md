# ml-platform

Hands-on implementations of the core components of a modern ML platform —
built to understand the systems and storage tradeoffs, not to wrap frameworks.

Recurring theme across every component: **write the logic once, swap the
infrastructure by configuration.** Feast (sqlite→Redis), Airflow (executor),
Ray (cluster), MLflow (backend) — a platform engineer builds that abstraction
so data scientists never touch infra.

## Components

| Component | Demonstrates | Status |
|-----------|--------------|--------|
| `feature_store/` | Offline/online stores, point-in-time correctness, training/serving skew, storage-tech tradeoffs | ✅ done  |
| `orchestration/` | Pipeline DAGs, retries, backfills (Airflow) |  ✅ done |
| `training/` | Distributed training (Ray) | ✅ done   ← Ray DDP, loss dropping, config-swap scaling |
| `registry/` | Model versioning, promotion, lineage (MLflow) | planned |
| `monitoring/` | Drift & skew detection (Evidently) | planned |

## Feature Store

Solves **training/serving skew**: a feature computed one way in batch training
and another way in real-time serving silently degrades a model in production.
The store is the single source of truth so both paths get identical values.

```
OFFLINE STORE                        ONLINE STORE
purpose: build training sets         purpose: serve features at inference
access:  high-throughput batch scan  access:  single-key point lookup
scale:   billions of rows            scale:   one entity at a time
latency: seconds-minutes fine        latency: single-digit milliseconds
tech:    Parquet / BigQuery /        tech:    Redis / DynamoDB /
         Snowflake / S3                       Cassandra
```

Key concepts demonstrated: point-in-time correctness (fetch features as-of the
event timestamp, never the latest value, to avoid data leakage), materialization
(offline→online sync), and the provider abstraction (same code, sqlite→Redis by
config).

Landscape: Feast (this build, precompute-and-materialize) vs Chalk (on-demand
resolver graph, optimized for freshness) vs Tecton (enterprise).

### Operational notes (learned debugging this)

- **Empty online store despite "successful" materialization** almost always
  means the materialization window didn't overlap the feature timestamps.
  `materialize-incremental <end>` scans from a recent start; if your data is
  older, it loads nothing and serving returns nulls — a silent failure with no
  error. Fix: `feast materialize <start> <end>` bracketing the actual data range.
  In production this is a real incident class — a drifted job window silently
  starves the online store and the model serves nulls.

- **Feast config paths are relative to the directory holding `feature_store.yaml`**,
  not to where you launch the command. Since `feast apply` runs from inside
  `feature_store/`, every path (registry, online store, source) drops the
  `feature_store/` prefix.

### How this runs in production

Infrastructure and feature definitions have separate lifecycles. Infra (registry
on RDS/S3, online store on Redis/DynamoDB, offline on S3+Athena) is provisioned
once as versioned IaC (CDK/Terraform). Feature definitions live in git and are
applied via `feast apply` in CI/CD on change — the same way schema migrations
run. Materialization is a separate scheduled job (cron/Airflow). Conflating
these — re-provisioning infra on every feature change — is the anti-pattern.

## Running

```bash
make gen-data        # synthetic user-event dataset
make apply           # register feature definitions with Feast
make train-retrieve  # point-in-time correct historical features -> training set
make materialize     # offline -> online sync
make serve-lookup    # online feature lookup (the serving path)
make swap-redis      # bring up Redis, repoint online store, re-materialize
```
