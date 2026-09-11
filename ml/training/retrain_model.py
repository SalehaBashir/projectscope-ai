from pathlib import Path
import subprocess
import sys
import joblib


BASE_DIR = Path(__file__).resolve().parents[2]

TRAIN_SCRIPT = BASE_DIR / "ml" / "training" / "train_model.py"
MODEL_PATH = BASE_DIR / "ml" / "models" / "effort_model.pkl"


def get_next_version():
    if not MODEL_PATH.exists():
        return "v1"

    bundle = joblib.load(MODEL_PATH)
    current_version = bundle.get("model_version", "v1")

    current_number = int(current_version.replace("v", ""))
    return f"v{current_number + 1}"


def retrain_model():
    next_version = get_next_version()

    print(f"Starting model retraining: {next_version}")

    result = subprocess.run(
        [sys.executable, str(TRAIN_SCRIPT)],
        check=True,
    )

    if result.returncode == 0:
        bundle = joblib.load(MODEL_PATH)
        bundle["model_version"] = next_version

        joblib.dump(bundle, MODEL_PATH)

        print(f"Model retraining completed successfully: {next_version}")


if __name__ == "__main__":
    retrain_model()