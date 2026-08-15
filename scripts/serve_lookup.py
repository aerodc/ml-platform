"""The ONLINE path: fetch the latest features for a user, fast.

What a model server calls at inference. Reads from the online store (sqlite now,
redis later) with a single-key lookup. Values here must equal what training saw
for the same feature definition — that equality IS the no-skew guarantee.
"""
from feast import FeatureStore


def main(user_ids=(0, 1, 2)):
    store = FeatureStore(repo_path="feature_store")
    feats = store.get_online_features(
        features=["user_features:clicks_7d", "user_features:click_rate_7d"],
        entity_rows=[{"user_id": u} for u in user_ids],
    ).to_dict()
    print(feats)


if __name__ == "__main__":
    main()
