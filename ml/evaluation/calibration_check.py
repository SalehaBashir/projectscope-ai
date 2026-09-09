import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "projects_processed.csv",
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "effort_model.pkl",
)

RESULT_PATH = os.path.join(
    BASE_DIR,
    "evaluation",
    "calibration_results.json",
)


def main():
    print("ML Prediction Calibration Check")
    print("--------------------------------")

    df = pd.read_csv(DATA_PATH)

    bundle = joblib.load(MODEL_PATH)

    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    X = df[feature_columns]
    y = df["actual_hours"]

    predictions = model.predict(X)

    errors = np.abs(y.to_numpy() - predictions)

    mae = mean_absolute_error(y, predictions)

    mean_actual = float(np.mean(y))
    mean_predicted = float(np.mean(predictions))

    mean_error = mean_predicted - mean_actual

    calibration_ratio = (
        mean_predicted / mean_actual
        if mean_actual != 0
        else 0.0
    )

    results = {
        "model_name": bundle["model_name"],
        "num_samples": int(len(y)),
        "mean_actual_hours": round(mean_actual, 2),
        "mean_predicted_hours": round(mean_predicted, 2),
        "mean_prediction_error_hours": round(mean_error, 2),
        "calibration_ratio": round(calibration_ratio, 4),
        "mae_hours": round(float(mae), 2),
        "mean_absolute_error_hours": round(float(np.mean(errors)), 2),
    }

    with open(RESULT_PATH, "w") as file:
        json.dump(results, file, indent=2)

    print(f"Mean actual effort:      {mean_actual:.2f} hours")
    print(f"Mean predicted effort:   {mean_predicted:.2f} hours")
    print(f"Mean prediction error:   {mean_error:.2f} hours")
    print(f"Calibration ratio:       {calibration_ratio:.4f}")
    print(f"MAE:                     {mae:.2f} hours")

    print()
    print(f"Results saved to: {RESULT_PATH}")


if __name__ == "__main__":
    main()