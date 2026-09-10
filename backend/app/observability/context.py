"""
Request-scoped context for observability.
"""
from contextvars import ContextVar
from typing import Optional

model_version_ctx: ContextVar[Optional[str]] = ContextVar("model_version_ctx", default=None)
prompt_tokens_ctx: ContextVar[Optional[int]] = ContextVar("prompt_tokens_ctx", default=None)
completion_tokens_ctx: ContextVar[Optional[int]] = ContextVar("completion_tokens_ctx", default=None)
estimated_ai_cost_ctx: ContextVar[Optional[float]] = ContextVar("estimated_ai_cost_ctx", default=None)


def reset_ai_context():
    model_version_ctx.set(None)
    prompt_tokens_ctx.set(None)
    completion_tokens_ctx.set(None)
    estimated_ai_cost_ctx.set(None)


def set_ai_context(model: str, prompt_tokens: int, completion_tokens: int, estimated_cost: float):
    model_version_ctx.set(model)
    prompt_tokens_ctx.set(prompt_tokens)
    completion_tokens_ctx.set(completion_tokens)
    estimated_ai_cost_ctx.set(estimated_cost)