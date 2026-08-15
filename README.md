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
| `feature_store/` | Offline/online stores, point-in-time correctness, training/serving skew, storage-tech tradeoffs | in progress |
| `orchestration/` | Pipeline DAGs, retries, backfills (Airflow) | planned |
| `training/` | Distributed training (Ray) | planned |
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

## Running

```bash
make gen-data        # synthetic user-event dataset
make apply           # register feature definitions with Feast
make train-retrieve  # point-in-time correct historical features -> training set
make materialize     # offline -> online sync
make serve-lookup    # online feature lookup (the serving path)
make swap-redis      # bring up Redis, repoint online store, re-materialize
```
