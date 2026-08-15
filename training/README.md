# training — Ray Train

Distributed model training. Takes a single-node PyTorch training loop and scales
it across workers with Ray Train — the open-source equivalent of distributed
training on EMR/Spark.

## The core idea

Distributed data-parallel (DDP): each worker holds a model replica and a shard
of the data; gradients are synchronized across workers every step so all
replicas stay identical. Ray Train orchestrates the workers; your training loop
barely changes.

Going from single-node to distributed is two wrappers:
- `prepare_model()` — wraps the model in DistributedDataParallel (gradient sync)
- `prepare_data_loader()` — shards the data so each worker sees a different slice

## The config-swap theme

`ScalingConfig(num_workers=2)` runs 2 worker processes on a laptop;
`num_workers=8, use_gpu=True` runs on a GPU cluster — **same training code**.
This is the same "write logic once, swap infra by config" pattern as the
feature store's online-store swap and Airflow's executor.

## On CPU

Run locally with multiple CPU workers to see the DDP mechanics (data sharding,
gradient sync, metric aggregation) — no real speedup without a cluster, but the
distributed structure is identical to what runs at scale.

## Landscape

Ray Train vs alternatives: PyTorch DDP raw (more manual), Horovod (older),
SageMaker/Vertex managed training (cloud-locked). Ray chosen for a unified
API across training + serving + tuning and a clean local-to-cluster story.

## Running

```bash
pip install "ray[train]" torch
python -m training.train_ray
```

Wired into the Airflow `train` task and the capstone pipeline later.
