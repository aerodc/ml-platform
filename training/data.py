"""Load the synthetic user features into tensors.

Reuses the feature-store data — the model predicts `converted` from the same
features the feature store serves. This keeps the whole platform coherent:
features flow feature_store -> training.
"""
import pandas as pd
import numpy as np
import torch
from torch.utils.data import TensorDataset
from pathlib import Path

FEATURES = ["clicks_7d", "click_rate_7d"]

ROOT = Path(__file__).resolve().parent.parent

def load_dataset(features_path=None,
                 labels_path=None):
    features_path = features_path or ROOT / "feature_store/data/user_features.parquet"
    labels_path = labels_path or ROOT / "feature_store/data/training_labels.parquet"             
    feats = pd.read_parquet(features_path)
    labels = pd.read_parquet(labels_path)

    # join each label to that user's most recent feature snapshot at/before the event
    # (a simplified point-in-time join — the real one lives in the feature store)
    merged = pd.merge_asof(
        labels.sort_values("event_timestamp"),
        feats.sort_values("event_timestamp"),
        by="user_id",
        on="event_timestamp",
        direction="backward",
    ).dropna(subset=FEATURES)

    X = torch.tensor(merged[FEATURES].values, dtype=torch.float32)
    y = torch.tensor(merged["converted"].values, dtype=torch.float32).unsqueeze(1)
    return TensorDataset(X, y), len(FEATURES)
