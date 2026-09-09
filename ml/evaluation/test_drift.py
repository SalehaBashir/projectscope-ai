import os
import pandas as pd

from drift_check import calculate_psi, interpret_psi


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "projects_processed.csv",
)


FEATURE_COLUMNS = [
    "num_features",
    "num_tasks",
    "num_roles",
    "has_payment",
    "has_admin",
    "has_mobile",
    "has_realtime",
    "num_integrations",
    "complexity_score",
]


def test_drift_detection():
    reference_df = pd.read_csv(DATA_PATH)

    # Create an artificial "current" dataset
    # with a deliberate distribution shift.
    current_df = reference_df.copy()

    current_df["num_features"] = current_df["num_features"] * 3
    current_df["num_tasks"] = current_df["num_tasks"] * 3
    current_df["complexity_score"] = current_df["complexity_score"] + 5

    detected_features = []

    for feature in FEATURE_COLUMNS:
        psi = calculate_psi(
            reference_df[feature],
            current_df[feature],
        )

        print(
            f"{feature}: "
            f"PSI={psi:.4f} "
            f"({interpret_psi(psi)})"
        )

        if psi >= 0.25:
            detected_features.append(feature)

    assert len(detected_features) > 0

    print()
    print("Drift detection test: PASSED")
    print("Drifted features:", detected_features)