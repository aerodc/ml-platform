"""Build a training set with POINT-IN-TIME CORRECT features (the offline path).

For each (user, event_timestamp, label) row, fetch feature values AS OF that
timestamp — not the latest. Getting this wrong = data leakage = a model that
looks great offline and fails in production.
"""
import pandas as pd
from feast import FeatureStore


def main():
    store = FeatureStore(repo_path="feature_store")
    entity_df = pd.read_parquet("feature_store/data/training_labels.parquet")

    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=["user_features:clicks_7d", "user_features:click_rate_7d"],
    ).to_df()

    print(training_df.head(10))
    print("shape:", training_df.shape)


if __name__ == "__main__":
    main()
