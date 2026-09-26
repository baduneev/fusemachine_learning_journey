"""Train, compare, register, and promote three churn classifiers with MLflow."""
import argparse
import json
from pathlib import Path
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from mlflow.models import infer_signature
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, f1_score,
                             precision_score, recall_score, roc_auc_score,
                             RocCurveDisplay)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.common import MODEL_NAME, OUTPUT, ROOT, TARGET, TRACKING_URI, features, load_telco


CONFIGS = [
    {"run_name": "logistic_c_0_5", "family": "logistic", "C": 0.5, "penalty": "l2"},
    {"run_name": "logistic_c_2", "family": "logistic", "C": 2.0, "penalty": "l2"},
    {"run_name": "random_forest_300_depth_8", "family": "random_forest", "n_estimators": 300, "max_depth": 8, "min_samples_leaf": 3},
]


def build_pipeline(X, config):
    categorical = X.select_dtypes(exclude="number").columns.tolist()
    numeric = X.select_dtypes(include="number").columns.tolist()
    prep = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    if config["family"] == "logistic":
        model = LogisticRegression(C=config["C"], penalty=config["penalty"], solver="liblinear",
                                   class_weight="balanced", max_iter=1000, random_state=42)
    else:
        model = RandomForestClassifier(n_estimators=config["n_estimators"], max_depth=config["max_depth"],
                                       min_samples_leaf=config["min_samples_leaf"], class_weight="balanced",
                                       random_state=42, n_jobs=-1)
    return Pipeline([("preprocess", prep), ("classifier", model)])


def save_plots(model, X_test, y_test, destination):
    destination.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, ax=ax, cmap="Blues", colorbar=False)
    fig.tight_layout(); fig.savefig(destination / "confusion_matrix.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5, 4))
    RocCurveDisplay.from_estimator(model, X_test, y_test, ax=ax)
    fig.tight_layout(); fig.savefig(destination / "roc_curve.png", dpi=160); plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-uri", default=TRACKING_URI)
    args = parser.parse_args()
    OUTPUT.mkdir(exist_ok=True)
    frame = load_telco()
    X, y = features(frame)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, stratify=y, random_state=42)
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment("telco-churn-model-comparison")
    rows = []
    for config in CONFIGS:
        with mlflow.start_run(run_name=config["run_name"]) as run:
            model = build_pipeline(X_train, config)
            started = time.perf_counter(); model.fit(X_train, y_train); seconds = time.perf_counter() - started
            prediction = model.predict(X_test)
            probability = model.predict_proba(X_test)[:, 1]
            metrics = {
                "accuracy": accuracy_score(y_test, prediction),
                "precision": precision_score(y_test, prediction),
                "recall": recall_score(y_test, prediction),
                "f1": f1_score(y_test, prediction),
                "roc_auc": roc_auc_score(y_test, probability),
                "train_seconds": seconds,
            }
            params = {**config, "random_state": 42, "test_fraction": .25, "class_weight": "balanced"}
            mlflow.log_params(params); mlflow.log_metrics(metrics)
            art = OUTPUT / "run_artifacts" / config["run_name"]
            save_plots(model, X_test, y_test, art)
            mlflow.log_artifacts(str(art), artifact_path="evaluation")
            signature = infer_signature(X_train.head(20), model.predict(X_train.head(20)))
            mlflow.sklearn.log_model(model, "model", signature=signature,
                                     input_example=X_train.head(3), registered_model_name=None)
            rows.append({"run_id": run.info.run_id, **config, **metrics})
    comparison = pd.DataFrame(rows).sort_values(["roc_auc", "f1"], ascending=False).reset_index(drop=True)
    comparison.to_csv(OUTPUT / "run_comparison.csv", index=False)
    (OUTPUT / "run_comparison.md").write_text(comparison.to_markdown(index=False, floatfmt=".4f") + "\n", encoding="utf-8")
    best = comparison.iloc[0]
    version = mlflow.register_model(f"runs:/{best.run_id}/model", MODEL_NAME, await_registration_for=60)
    client = MlflowClient()
    transitions = []
    for stage in ("Staging", "Production"):
        moved = client.transition_model_version_stage(MODEL_NAME, version.version, stage,
                                                      archive_existing_versions=(stage == "Production"))
        transitions.append({"stage": moved.current_stage, "timestamp_utc": pd.Timestamp.now(tz="UTC").isoformat()})
    client.set_registered_model_alias(MODEL_NAME, "champion", version.version)
    registry = {"model_name": MODEL_NAME, "version": version.version, "source_run_id": best.run_id,
                "selection_rule": "highest ROC-AUC, then F1", "winning_metrics": {
                    key: float(best[key]) for key in ("accuracy", "precision", "recall", "f1", "roc_auc")},
                "stage_transitions": transitions, "alias": "champion"}
    (OUTPUT / "registry_info.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")
    with mlflow.start_run(run_id=best.run_id):
        mlflow.log_artifact(str(OUTPUT / "run_comparison.csv"), artifact_path="comparison")
        mlflow.log_artifact(str(OUTPUT / "registry_info.json"), artifact_path="registry")
    print(comparison.to_string(index=False))
    print(f"Registered {MODEL_NAME} version {version.version}: Staging -> Production; alias=champion")


if __name__ == "__main__":
    main()
