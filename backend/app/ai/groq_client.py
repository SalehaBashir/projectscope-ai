from app.ai.provider import AIProvider
import logging
import os
import time

from groq import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)
from dotenv import load_dotenv

load_dotenv()


MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = os.getenv(
    "AI_FALLBACK_MODEL",
    "openai/gpt-oss-20b",
)

CLIENT_VERSION = "groq-client-v1.1"

MAX_TOKENS = 2000
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1

_client = None

logger = logging.getLogger("projectscope.ai")
logger.setLevel(logging.INFO)


def _get_client():
    """Lazily initialise the Groq client."""

    global _client

    if _client is None:
        api_key = os.getenv("AI_PROVIDER_API_KEY")

        if not api_key:
            raise RuntimeError(
                "AI_PROVIDER_API_KEY environment variable is required to call the LLM"
            )

        from groq import Groq

        _client = Groq(
            api_key=api_key,
            timeout=30.0,
        )

    return _client


def _request_model(
    client,
    model: str,
    system_prompt: str,
    user_prompt: str,
):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=MAX_TOKENS,
        response_format={"type": "json_object"},
    )


def call_llm_with_metadata(
    system_prompt: str,
    user_prompt: str,
) -> tuple[str, dict]:
    """Call the primary model and fall back to a secondary model if needed."""

    start_time = time.perf_counter()
    client = _get_client()

    models = [
        (MODEL, False),
        (FALLBACK_MODEL, True),
    ]

    last_exception = None

    for model, fallback_used in models:
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = _request_model(
                    client,
                    model,
                    system_prompt,
                    user_prompt,
                )

                duration_ms = round(
                    (time.perf_counter() - start_time) * 1000,
                    2,
                )

                usage = getattr(response, "usage", None)

                metadata = {
                    "provider": "groq",
                    "model": model,
                    "version": CLIENT_VERSION,
                    "attempt": attempt + 1,
                    "latency_ms": duration_ms,
                    "prompt_tokens": getattr(
                        usage,
                        "prompt_tokens",
                        None,
                    ),
                    "completion_tokens": getattr(
                        usage,
                        "completion_tokens",
                        None,
                    ),
                    "total_tokens": getattr(
                        usage,
                        "total_tokens",
                        None,
                    ),
                    "status": "success",
                    "fallback_used": fallback_used,
                }

                logger.info(
                    "llm_request_completed | "
                    f"provider=groq | "
                    f"model={model} | "
                    f"fallback_used={fallback_used} | "
                    f"attempt={attempt + 1}"
                )

                return response.choices[0].message.content, metadata

            except (
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
                RateLimitError,
            ) as exc:

                last_exception = exc

                if attempt >= MAX_RETRIES:
                    logger.warning(
                        "llm_model_exhausted | "
                        f"provider=groq | "
                        f"model={model} | "
                        f"fallback_used={fallback_used}"
                    )
                    break

                backoff = RETRY_BACKOFF_SECONDS * (2**attempt)

                logger.warning(
                    "llm_request_retry | "
                    f"provider=groq | "
                    f"model={model} | "
                    f"attempt={attempt + 1} | "
                    f"retry_in_seconds={backoff}"
                )

                time.sleep(backoff)

    logger.exception(
        "llm_request_failed_after_fallback | "
        f"primary_model={MODEL} | "
        f"fallback_model={FALLBACK_MODEL}"
    )

    raise last_exception


def call_llm(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Call the LLM with automatic fallback support."""

    raw_response, _ = call_llm_with_metadata(
        system_prompt,
        user_prompt,
    )

    return raw_response


class GroqProvider(AIProvider):
    """Groq implementation of the AI provider interface."""

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return call_llm(
            system_prompt,
            user_prompt,
        )