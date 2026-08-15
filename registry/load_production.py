"""Load whatever model is currently in Production — by STAGE, not version.

This is how serving fetches the model: it asks for "Production", and gets
whichever version was last promoted. Promoting a new model changes what this
returns with zero code change — the registry is the indirection layer.
"""
import mlflow.pytorch


def load_production(model_name: str = "conversion_model"):
    model = mlflow.pytorch.load_model(f"models:/{model_name}/Production")
    print("loaded Production model:", type(model))
    return model


if __name__ == "__main__":
    load_production()
