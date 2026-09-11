from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "processed",
    "projects_processed.csv",
)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURE_COLUMNS = [
    "num_features", "num_tasks", "num_roles", "has_payment",
    "has_admin", "has_mobile", "has_realtime", "num_integrations", "complexity_score",
]
TARGET_COLUMN = "actual_hours"

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Baseline: naive mean prediction
naive_pred = np.full_like(y_test, y_train.mean(), dtype=float)
naive_mae = mean_absolute_error(y_test, naive_pred)
print(f"\nNaive baseline (mean) MAE: {naive_mae:.1f} hours")

# Model 1: Linear Regression
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)
lr_mae = mean_absolute_error(y_test, lr_pred)
lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))
lr_r2 = r2_score(y_test, lr_pred)
print(f"\nLinear Regression:")
print(f"  MAE:  {lr_mae:.1f} hours")
print(f"  RMSE: {lr_rmse:.1f} hours")
print(f"  R^2:  {lr_r2:.3f}")

# Model 2: Random Forest
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_mae = mean_absolute_error(y_test, rf_pred)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
rf_r2 = r2_score(y_test, rf_pred)
print(f"\nRandom Forest:")
print(f"  MAE:  {rf_mae:.1f} hours")
print(f"  RMSE: {rf_rmse:.1f} hours")
print(f"  R^2:  {rf_r2:.3f}")

# Pick the better model
if rf_mae < lr_mae:
    best_model, best_name = rf, "RandomForest"
else:
    best_model, best_name = lr, "LinearRegression"

print(f"\nBest model: {best_name}")

model_path = os.path.join(MODEL_DIR, "effort_model.pkl")

joblib.dump(
    {
        "model": best_model,
        "scaler": scaler,
        "feature_columns": FEATURE_COLUMNS,
        "model_name": best_name,
        "model_version": "v1",
    },
    model_path,
)

print(f"Saved model to {model_path}")