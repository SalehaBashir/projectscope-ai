import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from app.ai import groq_client
from app.ai.groq_client import call_llm_with_metadata
from app.ai.prompts import REQUIREMENT_ANALYZER_SYSTEM_PROMPT
from app.schemas.requirement_analysis import RequirementAnalysisResult


def test_schema_accepts_valid_result():
    result = RequirementAnalysisResult(
        project_type="ecommerce",
        users=["customer"],
        requirements=[
            {
                "category": "functional",
                "text": "Customers can browse products",
                "confidence": 0.95,
            }
        ],
        features=[
            {
                "canonical_name": "PRODUCT_BROWSING",
                "description": "Browse products",
                "priority": "high",
                "complexity": "medium",
                "confidence": 0.95,
            }
        ],
        assumptions=[],
        missing_information=[],
    )

    assert result.project_type == "ecommerce"
    assert result.features[0].confidence == 0.95


def test_schema_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        RequirementAnalysisResult(
            project_type="ecommerce",
            users=["customer"],
            requirements=[],
            features=[
                {
                    "canonical_name": "PRODUCT_BROWSING",
                    "description": "Browse products",
                    "priority": "high",
                    "complexity": "medium",
                    "confidence": 1.5,
                }
            ],
        )


def test_schema_rejects_empty_requirement_text():
    with pytest.raises(ValidationError):
        RequirementAnalysisResult(
            project_type="ecommerce",
            users=["customer"],
            requirements=[
                {
                    "category": "functional",
                    "text": "",
                    "confidence": 0.9,
                }
            ],
            features=[],
        )


def test_prompt_contains_injection_protection():
    prompt = REQUIREMENT_ANALYZER_SYSTEM_PROMPT.lower()

    assert "untrusted" in prompt
    assert "ignore" in prompt
    assert "system prompt" in prompt
    assert "api key" in prompt


@patch("app.ai.groq_client.time.sleep")
@patch("app.ai.groq_client._get_client")
def test_llm_metadata(mock_get_client, mock_sleep):
    choice = MagicMock()

    choice.message.content = json.dumps(
        {
            "project_type": "ecommerce",
            "users": ["customer"],
            "requirements": [],
            "features": [],
            "assumptions": [],
            "missing_information": [],
        }
    )

    response = MagicMock()
    response.choices = [choice]

    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 20
    response.usage.total_tokens = 30

    client = MagicMock()
    client.chat.completions.create.return_value = response
    mock_get_client.return_value = client

    raw_response, metadata = call_llm_with_metadata(
        "system",
        "user",
    )

    assert json.loads(raw_response)["project_type"] == "ecommerce"
    assert metadata["provider"] == "groq"
    assert metadata["model"]
    assert metadata["version"]
    assert metadata["prompt_tokens"] == 10
    assert metadata["completion_tokens"] == 20
    assert metadata["total_tokens"] == 30
    assert metadata["status"] == "success"
    assert metadata["fallback_used"] is False


@patch("app.ai.groq_client.time.sleep")
@patch("app.ai.groq_client._get_client")
@patch("app.ai.groq_client._request_model")
def test_llm_fallback_model(mock_request_model, mock_get_client, mock_sleep):
    class TransientError(Exception):
        pass

    choice = MagicMock()

    choice.message.content = json.dumps(
        {
            "project_type": "ecommerce",
            "users": ["customer"],
            "requirements": [],
            "features": [],
            "assumptions": [],
            "missing_information": [],
        }
    )

    fallback_response = MagicMock()
    fallback_response.choices = [choice]

    fallback_response.usage.prompt_tokens = 10
    fallback_response.usage.completion_tokens = 20
    fallback_response.usage.total_tokens = 30

    client = MagicMock()
    mock_get_client.return_value = client

    mock_request_model.side_effect = [
        TransientError("Primary model failed"),
        fallback_response,
    ]

    with patch("app.ai.groq_client.APIConnectionError", TransientError):
        with patch("app.ai.groq_client.MAX_RETRIES", 0):
            raw_response, metadata = groq_client.call_llm_with_metadata(
                "system",
                "user",
            )

    assert json.loads(raw_response)["project_type"] == "ecommerce"
    assert metadata["provider"] == "groq"
    assert metadata["fallback_used"] is True
    assert metadata["model"] == "openai/gpt-oss-20b"
    assert mock_request_model.call_count == 2