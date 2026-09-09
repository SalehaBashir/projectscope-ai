import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

RAW_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "synthetic_projects.csv",
)

REAL_FEEDBACK_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "real_feedback.csv",
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed",
)

PROCESSED_PATH = os.path.join(
    PROCESSED_DIR,
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

TARGET_COLUMN = "actual_hours"


def main():
    print("Loading raw dataset...")

    df = pd.read_csv(RAW_PATH)

    # Optionally merge real feedback-derived rows exported from the backend.
    if os.path.exists(REAL_FEEDBACK_PATH):
        real_df = pd.read_csv(REAL_FEEDBACK_PATH)
        if not real_df.empty:
            df = pd.concat([df, real_df], ignore_index=True)
            print(
                f"Merged {len(real_df)} real feedback rows from "
                f"{REAL_FEEDBACK_PATH}"
            )

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print(f"Loaded {len(df)} records.")

    # Keep only the columns required for ML.
    df = df[required_columns].copy()

    # Convert all ML columns to numeric values.
    for column in required_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Check for invalid/missing values.
    missing_values = df.isna().sum()

    if missing_values.any():
        print("\nMissing/invalid values found:")
        print(missing_values[missing_values > 0])

        raise ValueError(
            "Dataset contains missing or invalid values."
        )

    # Validate target values.
    if (df[TARGET_COLUMN] <= 0).any():
        raise ValueError(
            "actual_hours must contain only positive values."
        )

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    df.to_csv(PROCESSED_PATH, index=False)

    print("\nPreprocessing completed successfully.")
    print(f"Processed dataset saved to:")
    print(PROCESSED_PATH)
    print(f"Final shape: {df.shape}")


if __name__ == "__main__":
    main()