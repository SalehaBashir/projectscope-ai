import os

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "synthetic_projects.csv",
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "effort_model.pkl",
)


def main():
    df = pd.read_csv(DATA_PATH)

    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    X = df[feature_columns]
    y = df["actual_hours"]

    predictions = model.predict(X)

    ml_mae = mean_absolute_error(
        y,
        predictions,
    )

    ml_rmse = mean_squared_error(
        y,
        predictions,
    ) ** 0.5

    # Historical validation for the ML component.
    # The deterministic rule engine requires task-level base_hours,
    # which are not present in synthetic_projects.csv.
    # Therefore we do not fabricate a rule estimate.
    #
    # For this validation dataset, hybrid falls back to the ML estimate
    # because no valid historical rule estimate is available.

    hybrid_predictions = predictions

    hybrid_mae = mean_absolute_error(
        y,
        hybrid_predictions,
    )

    hybrid_rmse = mean_squared_error(
        y,
        hybrid_predictions,
    ) ** 0.5

    print("Phase 17 - Historical Validation")
    print("--------------------------------")
    print(f"Dataset: {os.path.basename(DATA_PATH)}")
    print(f"Samples: {len(df)}")
    print()
    print("ML:")
    print(f"  MAE:  {ml_mae:.2f} hours")
    print(f"  RMSE: {ml_rmse:.2f} hours")
    print()
    print("Hybrid:")
    print("  Rule estimate: unavailable in historical CSV")
    print("  LLM estimate: unavailable in historical CSV")
    print(f"  MAE:  {hybrid_mae:.2f} hours")
    print(f"  RMSE: {hybrid_rmse:.2f} hours")
    print()
    print("Validation note:")
    print(
        "Hybrid validation currently uses the ML component because "
        "the historical dataset does not contain task-level inputs "
        "required to reproduce the deterministic rule estimate."
    )


if __name__ == "__main__":
    main()