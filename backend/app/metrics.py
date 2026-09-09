from prometheus_client import Counter, Histogram


# Total HTTP requests
HTTP_REQUESTS_TOTAL = Counter(
    "projectscope_http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)


# HTTP request duration
HTTP_REQUEST_DURATION = Histogram(
    "projectscope_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)


# Total HTTP errors
HTTP_ERRORS_TOTAL = Counter(
    "projectscope_http_errors_total",
    "Total number of HTTP 4xx and 5xx responses",
    ["method", "path", "status"],
)


# AI / LLM requests
AI_REQUESTS_TOTAL = Counter(
    "projectscope_ai_requests_total",
    "Total number of AI/LLM requests",
    ["provider", "model", "status"],
)


# AI / LLM request duration
AI_REQUEST_DURATION = Histogram(
    "projectscope_ai_request_duration_seconds",
    "AI/LLM request duration in seconds",
    ["provider", "model"],
)


# AI token usage
AI_TOKENS_TOTAL = Counter(
    "projectscope_ai_tokens_total",
    "Total AI/LLM tokens used",
    ["provider", "model", "token_type"],
)