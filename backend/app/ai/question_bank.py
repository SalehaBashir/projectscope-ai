QUESTION_BANK = [
    {
        "id": "accounts",
        "text": "Do customers need accounts (login/signup)?",
        "trigger_keywords": ["AUTH", "LOGIN", "ACCOUNT", "PROFILE"],
        "always_ask": False,
    },
    {
        "id": "payment_provider",
        "text": "Which payment provider is required (e.g. Stripe, PayPal, JazzCash)?",
        "trigger_keywords": ["PAYMENT"],
        "always_ask": False,
    },
    {
        "id": "admin_roles",
        "text": "Will admins have one role, or multiple admin roles with different permissions?",
        "trigger_keywords": ["ADMIN", "DASHBOARD"],
        "always_ask": False,
    },
    {
        "id": "mobile_app",
        "text": "Is a mobile application required, in addition to (or instead of) web?",
        "trigger_keywords": [],
        "always_ask": True,
    },
    {
        "id": "real_time_tracking",
        "text": "Is real-time tracking or live updates required?",
        "trigger_keywords": ["REAL_TIME", "TRACKING", "NOTIFICATION"],
        "always_ask": False,
    },
    {
        "id": "integrations",
        "text": "How many external integrations are needed (e.g. payment, maps, SMS, email)?",
        "trigger_keywords": ["PAYMENT", "MESSAGING", "SEARCH", "MAP"],
        "always_ask": False,
    },
    {
        "id": "scale",
        "text": "What traffic/scale is expected (e.g. hundreds vs. millions of users)?",
        "trigger_keywords": [],
        "always_ask": True,
    },
]