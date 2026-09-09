import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DIR = PROJECT_ROOT / "ml" / "evaluation"


def _load_json(filename):
    path = EVALUATION_DIR / filename
    assert path.exists(), f"Missing evaluation file: {path}"

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def test_model_metrics_exist_and_are_valid():
    metrics = _load_json("metrics.json")

    assert metrics["model_name"] in {
        "LinearRegression",
        "RandomForest",
    }

    assert metrics["num_test_samples"] > 0
    assert metrics["mae_hours"] >= 0
    assert metrics["rmse_hours"] >= 0
    assert -1 <= metrics["r2"] <= 1


def test_model_beats_basic_error_expectation():
    metrics = _load_json("metrics.json")

    # The trained model should provide useful predictive performance.
    assert metrics["mae_hours"] < 100
    assert metrics["rmse_hours"] < 120
    assert metrics["r2"] > 0.5


def test_drift_results_are_valid():
    results = _load_json("drift_results.json")

    assert results["method"] == "Population Stability Index (PSI)"
    assert "overall_drift_detected" in results
    assert "features" in results

    assert len(results["features"]) > 0

    for feature, result in results["features"].items():
        assert "psi" in result
        assert "status" in result
        assert result["psi"] >= 0

        assert result["status"] in {
            "No significant drift",
            "Moderate drift",
            "Significant drift",
        }


def test_current_dataset_has_no_significant_drift():
    results = _load_json("drift_results.json")

    assert results["overall_drift_detected"] is False

    for result in results["features"].values():
        assert result["psi"] < 0.25


def test_calibration_results_are_valid():
    results = _load_json("calibration_results.json")

    assert results["model_name"] in {
        "LinearRegression",
        "RandomForest",
    }

    assert results["num_samples"] > 0
    assert results["mean_actual_hours"] > 0
    assert results["mean_predicted_hours"] > 0

    assert results["mae_hours"] >= 0
    assert results["mean_absolute_error_hours"] >= 0

    assert results["calibration_ratio"] > 0


def test_model_calibration_is_close_to_actual_effort():
    results = _load_json("calibration_results.json")

    calibration_ratio = results["calibration_ratio"]

    # 1.0 means predicted average == actual average.
    # Accept a reasonable 10% deviation.
    assert 0.90 <= calibration_ratio <= 1.10


def test_calibration_prediction_error_is_reasonable():
    results = _load_json("calibration_results.json")

    assert abs(
        results["mean_prediction_error_hours"]
    ) < results["mean_actual_hours"] * 0.10