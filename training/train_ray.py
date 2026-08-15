"""Distributed training with Ray Train.

The whole lesson is here: the per-worker training loop is almost identical to
single-node PyTorch. Ray Train handles worker orchestration, data sharding, and
gradient sync. You scale by changing ONE number in ScalingConfig — same
"swap infra by config" theme as the feature store and Airflow executor.
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

import ray.train
from ray.train import ScalingConfig, Checkpoint
from ray.train.torch import TorchTrainer, prepare_model, prepare_data_loader

from training.model import ConversionModel
from training.data import load_dataset


def train_per_worker(config):
    """Runs on EACH worker. Ray injects the distributed context.

    Note what makes this distributed vs single-node — just two wrappers:
      prepare_model()       -> wraps model in DistributedDataParallel
      prepare_data_loader() -> shards data so each worker sees a different slice
    Everything else is a normal PyTorch loop.
    """
    dataset, n_features = load_dataset()
    loader = DataLoader(dataset, batch_size=config["batch_size"], shuffle=True)
    loader = prepare_data_loader(loader)          # <- shards across workers

    model = ConversionModel(n_features)
    model = prepare_model(model)                  # <- wraps in DDP, syncs grads

    loss_fn = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config["lr"])

    for epoch in range(config["epochs"]):
        model.train()
        total = 0.0
        for X, y in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(X), y)
            loss.backward()                       # DDP syncs gradients here
            optimizer.step()
            total += loss.item()

        # report metrics back to Ray (aggregated across workers)
        ray.train.report({"epoch": epoch, "loss": total / max(1, len(loader))})


def main(num_workers=2, epochs=10):
    trainer = TorchTrainer(
        train_loop_per_worker=train_per_worker,
        train_loop_config={"lr": 0.01, "batch_size": 16, "epochs": epochs},
        # THE config-swap: num_workers=2 on your laptop (2 CPU processes),
        # num_workers=8, use_gpu=True on a cluster. Training code unchanged.
        scaling_config=ScalingConfig(num_workers=num_workers, use_gpu=False),
    )
    result = trainer.fit()
    print("final metrics:", result.metrics)


if __name__ == "__main__":
    main(num_workers=4)
