"""Simulate 'current' (production) data to compare against the training reference.

Real monitoring compares live serving data against the training distribution.
Here we synthesize a 'current' window: some features drift, some don't, so the
drift report has something real to catch.
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "monitoring" / "data"
OUT.mkdir(parents=True, exist_ok=True)

ref = pd.read_parquet(ROOT / "feature_store/data/user_features.parquet")

# reference = a slice of training data (the distribution the model knows)
reference = ref[["clicks_7d", "click_rate_7d"]].copy()

# current = production-like data with DELIBERATE drift on clicks_7d
rng = np.random.default_rng(42)
n = len(reference)
current = pd.DataFrame({
    # clicks_7d drifts UP (users clicking more than at training time)
    "clicks_7d": reference["clicks_7d"].values + rng.integers(5, 20, n),
    # click_rate_7d stays roughly stable (no real drift)
    "click_rate_7d": reference["click_rate_7d"].values + rng.normal(0, 0.005, n),
})

reference.to_parquet(OUT / "reference.parquet", index=False)
current.to_parquet(OUT / "current.parquet", index=False)
print(f"reference: {len(reference)} rows, current: {len(current)} rows")
print("clicks_7d deliberately drifted up; click_rate_7d stable")
