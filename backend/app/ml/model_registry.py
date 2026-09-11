from pathlib import Path
import joblib


BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_DIR = BASE_DIR / "ml" / "models"

ACTIVE_MODEL = "effort_model.pkl"
def get_active_model_path() -> Path:
    return MODEL_DIR / ACTIVE_MODEL


def load_active_model():
    model_path = get_active_model_path()

    if not model_path.exists():
        raise FileNotFoundError(
            f"Active model not found: {model_path}"
        )

    return joblib.load(model_path)


def get_model_info() -> dict:
    bundle = load_active_model()

    return {
        "model_name": bundle.get("model_name", "unknown"),
        "model_file": ACTIVE_MODEL,
        "feature_columns": bundle.get("feature_columns", []),
        "model_version": bundle.get("model_version", "v1"),
    }