"""Generate a synthetic user-event dataset for the feature store.

Per-user feature snapshots WITH timestamps (so point-in-time retrieval is
meaningful) plus a training label set at random past moments. The timestamps
are the whole point: a feature store returns a feature's value AS OF a past
moment, not its latest value.
"""
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(0)
OUT = Path("feature_store/data")
OUT.mkdir(parents=True, exist_ok=True)

N_USERS = 50
DAYS = 30
start = pd.Timestamp("2026-01-01")

rows = []
for user_id in range(N_USERS):
    click_rate = np.random.uniform(0.01, 0.2)
    for d in range(DAYS):
        ts = start + pd.Timedelta(days=d)
        click_rate = max(0.0, click_rate + np.random.normal(0, 0.01))
        rows.append({
            "user_id": user_id,
            "event_timestamp": ts,
            "clicks_7d": int(np.random.poisson(click_rate * 100)),
            "click_rate_7d": round(click_rate, 4),
        })
features = pd.DataFrame(rows)
features.to_parquet(OUT / "user_features.parquet", index=False)
print(f"wrote {len(features)} feature rows for {N_USERS} users over {DAYS} days")

train_rows = []
for _ in range(200):
    user_id = np.random.randint(0, N_USERS)
    day = np.random.randint(5, DAYS)
    ts = start + pd.Timedelta(days=day, hours=np.random.randint(0, 24))
    train_rows.append({
        "user_id": user_id,
        "event_timestamp": ts,
        "converted": int(np.random.rand() < 0.3),
    })
labels = pd.DataFrame(train_rows)
labels.to_parquet(OUT / "training_labels.parquet", index=False)
print(f"wrote {len(labels)} training label rows")
