"""End-to-end demo: train -> track -> register -> promote -> load by stage.

Ties the registry component to the real training component. Runs a quick
single-process training (not the full Ray job — that's wired in the capstone)
to produce a model, then exercises the full MLflow lifecycle.
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from training.model import ConversionModel
from training.data import load_dataset
from registry.tracking import log_run
from registry.promote import promote_latest
from registry.load_production import load_production


def quick_train(epochs=10):
    dataset, n_features = load_dataset()
    loader = DataLoader(dataset, batch_size=16, shuffle=True)
    model = ConversionModel(n_features)
    loss_fn = nn.BCEWithLogitsLoss()
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    final_loss = 0.0
    for _ in range(epochs):
        total = 0.0
        for X, y in loader:
            opt.zero_grad()
            loss = loss_fn(model(X), y)
            loss.backward()
            opt.step()
            total += loss.item()
        final_loss = total / len(loader)
    return model, {"lr": 0.01, "epochs": epochs, "batch_size": 16}, {"final_loss": final_loss}


if __name__ == "__main__":
    model, params, metrics = quick_train()
    log_run(model, params, metrics)     # track + register
    promote_latest()                    # Staging -> Production
    load_production()                   # load by stage
