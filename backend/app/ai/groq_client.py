import hashlib
import json
import redis as redis_lib
from app.observability.context import set_ai_context
from app.ai.provider import AIProvider
from app.metrics import (
    AI_REQUESTS_TOTAL,
    AI_REQUEST_DURATION,
    AI_TOKENS_TOTAL,
)
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
_cache_client = None


def _get_cache_client():
    global _cache_client
    if _cache_client is None:
        redis_url = os.getenv("REDIS_URL")
        _cache_client = redis_lib.from_url(redis_url, decode_responses=True) if redis_url else None
    return _cache_client


def _cache_key(system_prompt: str, user_prompt: str) -> str:
    raw = f"{system_prompt}|{user_prompt}"
    return "ai_cache:" + hashlib.sha256(raw.encode()).hexdigest()


def get_cached_response(system_prompt: str, user_prompt: str):
    client = _get_cache_client()
    if client is None:
        return None
    cached = client.get(_cache_key(system_prompt, user_prompt))
    return json.loads(cached) if cached else None


def set_cached_response(system_prompt: str, user_prompt: str, response: str, ttl_seconds: int = 86400):
    client = _get_cache_client()
    if client is None:
        return
    client.setex(_cache_key(system_prompt, user_prompt), ttl_seconds, json.dumps(response))

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
    # Phase 32: skip the LLM entirely if we've analyzed this exact
    # description before — saves cost and latency on repeated requests.
    cached = get_cached_response(system_prompt, user_prompt)
    if cached is not None:
        cached_content, cached_metadata = cached
        cached_metadata["cache_hit"] = True
        return cached_content, cached_metadata

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

                # Prometheus AI metrics
                AI_REQUESTS_TOTAL.labels(
                    provider="groq",
                    model=model,
                    status="success",
                ).inc()

                AI_REQUEST_DURATION.labels(
                    provider="groq",
                    model=model,
                ).observe(
                    time.perf_counter() - start_time
                )

                prompt_tokens = getattr(
                    usage,
                    "prompt_tokens",
                    0,
                ) or 0

                completion_tokens = getattr(
                    usage,
                    "completion_tokens",
                    0,
                ) or 0

                AI_TOKENS_TOTAL.labels(
                    provider="groq",
                    model=model,
                    token_type="prompt",
                ).inc(prompt_tokens)

                AI_TOKENS_TOTAL.labels(
                    provider="groq",
                    model=model,
                    token_type="completion",
                ).inc(completion_tokens)

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
                    "provider=groq | "
                    f"model={model} | "
                    f"fallback_used={fallback_used} | "
                    f"attempt={attempt + 1}"
                )

                metadata["cache_hit"] = False
                content = response.choices[0].message.content

                # Phase 32: cache this exact prompt's result for 24h
                set_cached_response(system_prompt, user_prompt, (content, metadata))

                return content, metadata

            except (
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
                RateLimitError,
            ) as exc:

                AI_REQUESTS_TOTAL.labels(
                    provider="groq",
                    model=model,
                    status="error",
                ).inc()

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