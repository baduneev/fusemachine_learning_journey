"""Shared paths and Telco data preparation."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "telco_customer_churn.csv"
OUTPUT = ROOT / "outputs"
MLRUNS_DB = ROOT / "mlruns.db"
TRACKING_URI = f"sqlite:///{MLRUNS_DB.as_posix()}"
MODEL_NAME = "TelcoChurnBest"
TARGET = "Churn"


def load_telco(path=DATA_PATH):
    frame = pd.read_csv(path)
    frame["TotalCharges"] = pd.to_numeric(frame["TotalCharges"], errors="coerce")
    frame["TotalCharges"] = frame["TotalCharges"].fillna(frame["TotalCharges"].median())
    frame[TARGET] = frame[TARGET].map({"No": 0, "Yes": 1}).astype(int)
    return frame


def features(frame):
    return frame.drop(columns=[TARGET, "customerID"]), frame[TARGET]

