"""MLflow tracking + registry wiring.

Two distinct MLflow concepts, kept separate so the roles are clear:
  - TRACKING: log params, metrics, artifacts per run -> lineage & comparison
  - REGISTRY: version a model + move it through stages (Staging -> Production)

Config-swap theme: MLFLOW_TRACKING_URI points at a local ./mlruns dir now, or a
remote tracking server + S3 artifact store in production. Same code either way.
"""
import mlflow
import mlflow.pytorch
import torch


def log_run(model, params, metrics, model_name="conversion_model", n_features=2):
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        for k, v in metrics.items():
            mlflow.log_metric(k, v)

        input_example = torch.randn(1, n_features)   # one sample row, 2 features

        mlflow.pytorch.log_model(
            pytorch_model=model,
            name="model",                # 'artifact_path' is deprecated -> use 'name'
            registered_model_name=model_name,
            serialization_format="pickle",     # <- avoids pt2 graph-tracing entirely
        )
        print(f"logged run {run.info.run_id}, registered under '{model_name}'")
        return run.info.run_id
