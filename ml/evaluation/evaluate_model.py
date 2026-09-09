import json
import os

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


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
    "metrics.json",
)


print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

print("Loading trained model...")
bundle = joblib.load(MODEL_PATH)

model = bundle["model"]
feature_columns = bundle["feature_columns"]
model_name = bundle["model_name"]

X = df[feature_columns]
y = df["actual_hours"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

metrics = {
    "model_name": model_name,
    "dataset": "synthetic_projects.csv",
    "test_size": 0.2,
    "random_state": 42,
    "mae_hours": round(float(mae), 2),
    "rmse_hours": round(float(rmse), 2),
    "r2": round(float(r2), 4),
    "num_test_samples": int(len(y_test)),
}

with open(RESULT_PATH, "w") as f:
    json.dump(metrics, f, indent=2)

print("\nModel Evaluation")
print("----------------")
print(f"Model: {model_name}")
print(f"MAE:   {mae:.2f} hours")
print(f"RMSE:  {rmse:.2f} hours")
print(f"R²:    {r2:.4f}")

print(f"\nMetrics saved to:")
print(RESULT_PATH)