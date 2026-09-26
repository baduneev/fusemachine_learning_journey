"""FastAPI service that loads the MLflow Production model."""
from typing import Any

from fastapi import FastAPI, HTTPException
import mlflow
import mlflow.pyfunc
import pandas as pd

from src.common import MODEL_NAME, TRACKING_URI

mlflow.set_tracking_uri(TRACKING_URI)
app = FastAPI(title="Telco Churn Production Model", version="1.0.0")
_model = None


def get_model():
    global _model
    if _model is None:
        _model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/Production")
    return _model


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME, "stage": "Production"}


@app.post("/predict")
def predict(records: list[dict[str, Any]]):
    if not records:
        raise HTTPException(400, "Provide at least one customer record")
    try:
        values = get_model().predict(pd.DataFrame(records))
    except Exception as exc:
        raise HTTPException(422, f"Invalid model input: {exc}") from exc
    return {"predictions": [int(v) for v in values]}

