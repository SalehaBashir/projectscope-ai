import json
import pytest
from pydantic import ValidationError

from app.services import ai_analysis_service
from app.services.ai_analysis_service import (
    analyze_project_description,
    AIAnalysisError,
)


def _fake_llm_response(overrides=None):
    """Build a deterministic, valid LLM response payload."""
    base = {
        "project_type": "ecommerce",
        "users": ["customer", "admin"],
        "requirements": [
            {
                "category": "functional",
                "text": "Customers can create accounts and log in.",
                "confidence": 0.95,
            }
        ],
        "features": [
            {
                "canonical_name": "AUTHENTICATION",
                "description": "Account creation and login",
                "priority": "high",
                "complexity": "medium",
                "confidence": 0.95,
            }
        ],
        "assumptions": [],
        "missing_information": [],
    }
    if overrides:
        base.update(overrides)
    return base


def _fake_metadata():
    return {
        "provider": "groq",
        "model": "openai/gpt-oss-120b",
        "prompt_tokens": 10,
        "completion_tokens": 10,
        "latency_ms": 5,
        "status": "success",
    }


class TestExtractionQuality:
    def test_valid_response_extracts_requirements_and_features(self, monkeypatch):
        payload = _fake_llm_response()

        def fake_call(system_prompt, user_prompt):
            return json.dumps(payload), _fake_metadata()

        monkeypatch.setattr(ai_analysis_service, "call_llm_with_metadata", fake_call)

        result = analyze_project_description("An online store for clothing.")

        assert result.project_type == "ecommerce"
        assert len(result.requirements) == 1
        assert result.requirements[0].category == "functional"
        assert len(result.features) == 1
        assert result.features[0].canonical_name == "AUTHENTICATION"


class TestMissingInformationDetection:
    def test_missing_information_is_propagated(self, monkeypatch):
        payload = _fake_llm_response(
            {
                "missing_information": [
                    "Target user count is not specified.",
                    "Payment provider is not specified.",
                ]
            }
        )

        def fake_call(system_prompt, user_prompt):
            return json.dumps(payload), _fake_metadata()

        monkeypatch.setattr(ai_analysis_service, "call_llm_with_metadata", fake_call)

        result = analyze_project_description("A marketplace app.")

        assert len(result.missing_information) == 2
        assert "Payment provider is not specified." in result.missing_information

    def test_no_missing_information_gives_empty_list(self, monkeypatch):
        payload = _fake_llm_response()

        def fake_call(system_prompt, user_prompt):
            return json.dumps(payload), _fake_metadata()

        monkeypatch.setattr(ai_analysis_service, "call_llm_with_metadata", fake_call)

        result = analyze_project_description("A simple todo app.")

        assert result.missing_information == []


class TestAssumptionsPropagation:
    def test_assumptions_are_propagated(self, monkeypatch):
        payload = _fake_llm_response(
            {"assumptions": ["Assuming a single default currency (USD)."]}
        )

        def fake_call(system_prompt, user_prompt):
            return json.dumps(payload), _fake_metadata()

        monkeypatch.setattr(ai_analysis_service, "call_llm_with_metadata", fake_call)

        result = analyze_project_description("A subscription billing app.")

        assert result.assumptions == ["Assuming a single default currency (USD)."]


class TestHallucinationResistance:
    def test_invalid_json_raises_analysis_error_not_silent_fabrication(
        self, monkeypatch
    ):
        def fake_call(system_prompt, user_prompt):
            return "this is not valid json {{{", _fake_metadata()

        monkeypatch.setattr(ai_analysis_service, "call_llm_with_metadata", fake_call)

        with pytest.raises(AIAnalysisError):
            analyze_project_description("A project with broken LLM output.")

    def test_schema_violation_raises_analysis_error(self, monkeypatch):
        # Missing required "project_type" field entirely -> should fail validation,
        # not silently produce a fabricated/default project_type.
        payload = _fake_llm_response()
        del payload["project_type"]

        def fake_call(system_prompt, user_prompt):
            return json.dumps(payload), _fake_metadata()

        monkeypatch.setattr(ai_analysis_service, "call_llm_with_metadata", fake_call)

        with pytest.raises(AIAnalysisError):
            analyze_project_description("A project missing project_type.")

    def test_blank_project_type_is_rejected(self, monkeypatch):
        # An empty/whitespace project_type must be rejected by the validator,
        # not accepted as a fabricated guess.
        payload = _fake_llm_response({"project_type": "   "})

        def fake_call(system_prompt, user_prompt):
            return json.dumps(payload), _fake_metadata()

        monkeypatch.setattr(ai_analysis_service, "call_llm_with_metadata", fake_call)

        with pytest.raises(AIAnalysisError):
            analyze_project_description("A project with a blank project type.")