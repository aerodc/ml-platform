"""A small model + the single-node training logic.

Deliberately simple (the point is the DISTRIBUTED infra, not the model): a
2-layer MLP predicting `converted` from the user features. Kept separate from
the Ray wiring so you can see exactly what changes to go distributed.
"""
import torch
import torch.nn as nn


class ConversionModel(nn.Module):
    def __init__(self, n_features: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, x):
        return self.net(x)  # logits; BCEWithLogitsLoss applies sigmoid
