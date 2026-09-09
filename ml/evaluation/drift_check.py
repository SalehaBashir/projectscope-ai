import os
import json
import pandas as pd
import numpy as np


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

REFERENCE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "projects_processed.csv",
)

CURRENT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "projects_processed.csv",
)

RESULT_PATH = os.path.join(
    BASE_DIR,
    "evaluation",
    "drift_results.json",
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


def calculate_psi(reference, current, bins=10):
    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)

    edges = np.percentile(reference, np.linspace(0, 100, bins + 1))
    edges = np.unique(edges)

    if len(edges) < 2:
        return 0.0

    reference_counts, _ = np.histogram(reference, bins=edges)
    current_counts, _ = np.histogram(current, bins=edges)

    reference_pct = reference_counts / len(reference)
    current_pct = current_counts / len(current)

    epsilon = 1e-6

    reference_pct = np.clip(reference_pct, epsilon, None)
    current_pct = np.clip(current_pct, epsilon, None)

    psi = np.sum(
        (current_pct - reference_pct)
        * np.log(current_pct / reference_pct)
    )

    return float(psi)


def interpret_psi(psi):
    if psi < 0.10:
        return "No significant drift"
    elif psi < 0.25:
        return "Moderate drift"
    else:
        return "Significant drift"


def main():
    print("ML Drift Detection")
    print("------------------")

    reference_df = pd.read_csv(REFERENCE_PATH)
    current_df = pd.read_csv(CURRENT_PATH)

    results = {}

    for feature in FEATURE_COLUMNS:
        psi = calculate_psi(
            reference_df[feature],
            current_df[feature],
        )

        results[feature] = {
            "psi": round(psi, 6),
            "status": interpret_psi(psi),
        }

        print(
            f"{feature}: "
            f"PSI={psi:.4f} "
            f"({interpret_psi(psi)})"
        )

    overall_drift = any(
        item["psi"] >= 0.25
        for item in results.values()
    )

    output = {
        "reference_dataset": os.path.basename(REFERENCE_PATH),
        "current_dataset": os.path.basename(CURRENT_PATH),
        "method": "Population Stability Index (PSI)",
        "thresholds": {
            "no_significant_drift": "< 0.10",
            "moderate_drift": "0.10 - 0.25",
            "significant_drift": ">= 0.25",
        },
        "overall_drift_detected": overall_drift,
        "features": results,
    }

    with open(RESULT_PATH, "w") as file:
        json.dump(output, file, indent=2)

    print()
    print(
        "Overall drift detected:",
        "YES" if overall_drift else "NO",
    )

    print()
    print(f"Results saved to: {RESULT_PATH}")


if __name__ == "__main__":
    main()