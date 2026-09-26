"""Inject controlled churn drift, generate Evidently reports, and log them to MLflow."""
import json

from evidently import ColumnMapping
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from evidently.metrics import ColumnDriftMetric
from evidently.report import Report
import mlflow
import numpy as np
from sklearn.model_selection import train_test_split

from src.common import OUTPUT, TARGET, TRACKING_URI, load_telco
from src.custom_metrics import MeanShiftMetric


def split_and_inject(frame):
    reference, current = train_test_split(frame, test_size=.30, stratify=frame[TARGET], random_state=42)
    reference, current = reference.copy(), current.copy()
    rng = np.random.default_rng(42)
    # Known synthetic feature drift: a strong charge shift plus a contract distribution skew.
    current["MonthlyCharges"] = (current["MonthlyCharges"] + rng.normal(35, 5, len(current))).clip(0)
    skew = rng.choice(current.index, size=int(.55 * len(current)), replace=False)
    current.loc[skew, "Contract"] = "Month-to-month"
    # Controlled target shift for TargetDriftPreset: flip 15% of non-churn labels.
    non_churn = current.index[current[TARGET] == 0]
    flip = rng.choice(non_churn, size=int(.15 * len(current)), replace=False)
    current.loc[flip, TARGET] = 1
    return reference, current


def find_drift_results(payload):
    found = {}
    for metric in payload.get("metrics", []):
        result = metric.get("result", {})
        column = result.get("column_name")
        if column and "drift_detected" in result:
            found[column] = {"drift_detected": bool(result["drift_detected"]),
                             "drift_score": result.get("drift_score")}
    return found


def main():
    OUTPUT.mkdir(exist_ok=True)
    reference, current = split_and_inject(load_telco())
    reference.to_csv(OUTPUT / "reference_sample.csv", index=False)
    current.to_csv(OUTPUT / "current_with_synthetic_drift.csv", index=False)
    mapping = ColumnMapping(target=TARGET, numerical_features=["tenure", "MonthlyCharges", "TotalCharges"],
                            categorical_features=["gender", "SeniorCitizen", "Partner", "Dependents",
                                                  "PhoneService", "MultipleLines", "InternetService",
                                                  "OnlineSecurity", "OnlineBackup", "DeviceProtection",
                                                  "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
                                                  "PaperlessBilling", "PaymentMethod"])
    report = Report(metrics=[
        DataDriftPreset(), TargetDriftPreset(),
        ColumnDriftMetric("MonthlyCharges"), ColumnDriftMetric("Contract"),
        ColumnDriftMetric(TARGET), MeanShiftMetric("MonthlyCharges"),
    ])
    report.run(reference_data=reference.drop(columns=["customerID"]),
               current_data=current.drop(columns=["customerID"]), column_mapping=mapping)
    report.save_html(str(OUTPUT / "evidently_drift_report.html"))
    payload = report.as_dict()
    (OUTPUT / "evidently_drift_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    custom = next(m["result"] for m in payload["metrics"]
                  if m["metric"].startswith("MeanShiftMetric"))
    drift = find_drift_results(payload)
    summary = {
        "engineered_changes": ["MonthlyCharges + Normal(35, 5)", "55% Contract set to Month-to-month",
                               "15% of full current population changed from non-churn to churn"],
        "specific_column_results": drift,
        "custom_mean_shift": custom,
        "reference_churn_rate": float(reference[TARGET].mean()),
        "current_churn_rate": float(current[TARGET].mean()),
        "recommended_action": "Investigate upstream billing/contract changes and retrain only after validation if drift persists.",
    }
    (OUTPUT / "drift_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    mlflow.set_tracking_uri(TRACKING_URI); mlflow.set_experiment("telco-churn-monitoring")
    with mlflow.start_run(run_name="synthetic-production-drift"):
        mlflow.log_params({"reference_share": .70, "current_share": .30,
                           "monthly_charge_shift": 35, "contract_skew_share": .55, "target_flip_share": .15})
        mlflow.log_metrics({"custom_monthly_charge_mean_shift": custom["absolute_shift"],
                            "custom_monthly_charge_relative_shift_pct": custom["relative_shift_pct"],
                            "reference_churn_rate": summary["reference_churn_rate"],
                            "current_churn_rate": summary["current_churn_rate"]})
        for name in ("evidently_drift_report.html", "evidently_drift_report.json", "drift_summary.json"):
            mlflow.log_artifact(str(OUTPUT / name), artifact_path="monitoring")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

