"""
Export real feedback-derived training rows from the backend database
into the ML dataset pipeline.

This connects to the Postgres database used by the backend, builds the same
feature vector consumed by the effort-estimation model for every project that
has submitted feedback, and writes the rows to:

    ml/data/raw/real_feedback.csv

The output uses the exact column schema of `synthetic_projects.csv`, so it can
be merged with the synthetic data and fed through the existing
preprocess -> train pipeline for future retraining.

Usage:
    python ml/data/raw/export_feedback.py
"""

import csv
import os
import sys

# Allow importing the backend `app` package from this standalone script.
BACKEND_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "backend"
)
sys.path.append(os.path.abspath(BACKEND_DIR))

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "real_feedback.csv")


def export_feedback_rows():
    from app.database.connection import SessionLocal
    from app.services.feedback_service import build_ml_training_rows

    db = SessionLocal()
    try:
        rows = build_ml_training_rows(db)
    finally:
        db.close()

    if not rows:
        print("No projects with feedback found. No export written.")
        return

    fieldnames = list(rows[0].keys())
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Exported {len(rows)} real feedback rows -> {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    export_feedback_rows()
