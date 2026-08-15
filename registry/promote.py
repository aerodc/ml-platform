"""Promote a registered model through stages: None -> Staging -> Production.

This is the SHIPPING GATE. A model is registered (version N), evaluated in
Staging, and only moved to Production once it passes. Serving then loads
"the Production model" by stage, never by a hardcoded version — so promoting a
new model swaps what serves with zero code change.
"""
import mlflow
from mlflow.tracking import MlflowClient


def promote_latest(model_name: str = "conversion_model"):
    client = MlflowClient()

    # find the newest version of this registered model
    versions = client.search_model_versions(f"name='{model_name}'")
    latest = max(versions, key=lambda v: int(v.version))
    print(f"latest version: {latest.version} (current stage: {latest.current_stage})")

    client.transition_model_version_stage(model_name, latest.version, "Staging")
    print(f"  moved v{latest.version} -> Staging")

    # (real life: run eval against the Staging model here)

    client.transition_model_version_stage(
        model_name, latest.version, "Production",
        archive_existing_versions=True,   # old Production -> Archived
    )
    print(f"  moved v{latest.version} -> Production")


if __name__ == "__main__":
    promote_latest()
