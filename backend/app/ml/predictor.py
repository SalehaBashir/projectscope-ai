import joblib
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "ml", "models", "effort_model.pkl"
)

_model_bundle = None


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def predict_effort_hours(features: dict) -> float:
    bundle = _load_model()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    row = [[features.get(col, 0) for col in feature_columns]]
    prediction = model.predict(row)[0]
    return round(float(prediction), 1)