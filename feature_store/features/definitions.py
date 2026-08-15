"""Feast feature definitions — the single source of truth both the training
path and the serving path resolve against. Define the feature ONCE here;
Feast guarantees both paths read the same values (skew prevention)."""
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Int64, Float32

user = Entity(name="user", join_keys=["user_id"])

user_source = FileSource(
    path="data/user_features.parquet",
    timestamp_field="event_timestamp",
)

user_features = FeatureView(
    name="user_features",
    entities=[user],
    ttl=timedelta(days=90),
    schema=[
        Field(name="clicks_7d", dtype=Int64),
        Field(name="click_rate_7d", dtype=Float32),
    ],
    source=user_source,
    online=True,
)
