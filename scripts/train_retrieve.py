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

    # TODO (you implement):
    #   training_df = store.get_historical_features(
    #       entity_df=entity_df,
    #       features=["user_features:clicks_7d", "user_features:click_rate_7d"],
    #   ).to_df()
    #   print(training_df.head()); print(training_df.shape)
    #
    #   LEARNING STEP — prove point-in-time correctness:
    #   pick one (user_id, event_timestamp) row and confirm the clicks_7d you
    #   got matches the feature snapshot dated ON OR BEFORE that timestamp in
    #   user_features.parquet — NOT a later one. Note it in the README.
    raise NotImplementedError


if __name__ == "__main__":
    main()
