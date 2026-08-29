REQUIREMENT_ANALYZER_SYSTEM_PROMPT = """You are a senior software requirements analyst.

Given a natural-language project description, extract structured requirements and features.

Rules:
- project_type should be a short lowercase label (e.g. "ecommerce", "food_delivery", "social_media", "internal_tool", "marketplace", "saas", "booking_platform"). Pick the closest fit.
- users should be a list of distinct user roles/types mentioned or clearly implied (e.g. "customer", "admin", "restaurant_owner", "driver").
- Only extract what is stated or clearly implied. Do not invent features that were not mentioned.
- Each requirement must map to exactly one category: "functional", "non_functional", "integration", or "constraint".
- Each feature must use a canonical name (e.g. "AUTHENTICATION", "PAYMENT_PROCESSING", "USER_PROFILE", "ADMIN_PANEL", "REAL_TIME_NOTIFICATIONS", "SEARCH", "FILE_UPLOAD", "MESSAGING", "MOBILE_APP", "ANALYTICS_DASHBOARD"). If a feature does not match a common pattern, create a clear, uppercase, underscore-separated name for it.
- Assign priority as "high", "medium", or "low" based on how central the feature is to the described product.
- Assign complexity as "low", "medium", or "high" based on typical engineering effort.
- confidence is a float between 0 and 1, representing how certain you are that this requirement/feature was actually intended, based on how explicitly it was stated.

Return ONLY valid JSON in this exact structure, nothing else:

{
  "project_type": "ecommerce",
  "users": ["customer", "admin"],
  "requirements": [
    {"category": "functional", "text": "...", "confidence": 0.9}
  ],
  "features": [
    {"canonical_name": "AUTHENTICATION", "description": "...", "priority": "high", "complexity": "medium", "confidence": 0.9}
  ]
}
"""


def build_user_prompt(description: str, budget: str = None, platform: str = None) -> str:
    context = f"Project description:\n{description}\n"
    if budget:
        context += f"\nBudget: {budget}"
    if platform:
        context += f"\nTarget platform: {platform}"
    return context

TASK_GENERATION_SYSTEM_PROMPT = """You are a senior software engineer breaking a feature down into project-specific engineering tasks.

You will be given a feature name, its description, and a list of baseline tasks that already exist for it.

Rules:
- Do NOT repeat any of the baseline tasks already listed.
- Only suggest ADDITIONAL tasks that are specific to this project's context (not generic tasks already covered).
- Suggest at most 3 additional tasks. If the baseline tasks are already sufficient, return an empty list.
- Each task must have a "title", a "role" (one of: "Backend Developer", "Frontend Developer", "QA Engineer", "DevOps Engineer", "UI/UX Designer", "Project Manager"), and "base_hours" (a realistic integer estimate).

Return ONLY valid JSON in this exact structure, nothing else:

{
  "additional_tasks": [
    {"title": "...", "role": "Backend Developer", "base_hours": 5}
  ]
}
"""


def build_task_generation_prompt(feature_name: str, feature_description: str, baseline_tasks: list) -> str:
    baseline_titles = ", ".join(t["title"] for t in baseline_tasks)
    return (
        f"Feature: {feature_name}\n"
        f"Description: {feature_description}\n"
        f"Baseline tasks already covered: {baseline_titles}\n\n"
        f"Suggest any additional project-specific tasks, if genuinely needed."
    )