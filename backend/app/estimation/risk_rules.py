RISK_TEMPLATES = [
    {
        "keyword": "PAYMENT",
        "description": "Payment processing carries fraud, chargeback, and compliance risk (e.g. PCI-DSS requirements).",
        "probability": "medium",
        "impact": "high",
        "mitigation": "Use a PCI-compliant payment provider (Stripe/PayPal), implement fraud detection, and avoid storing raw card data.",
    },
    {
        "keyword": "REAL_TIME",
        "description": "Real-time features (live tracking, notifications) can be difficult to scale reliably under load.",
        "probability": "medium",
        "impact": "medium",
        "mitigation": "Use a proven real-time infrastructure (WebSockets/managed pub-sub) and load-test before launch.",
    },
    {
        "keyword": "TRACKING",
        "description": "Real-time features (live tracking, notifications) can be difficult to scale reliably under load.",
        "probability": "medium",
        "impact": "medium",
        "mitigation": "Use a proven real-time infrastructure (WebSockets/managed pub-sub) and load-test before launch.",
    },
    {
        "keyword": "ADMIN",
        "description": "Admin/dashboard access control is a common source of security misconfigurations.",
        "probability": "low",
        "impact": "high",
        "mitigation": "Implement role-based access control and test permission boundaries explicitly.",
    },
    {
        "keyword": "DASHBOARD",
        "description": "Admin/dashboard access control is a common source of security misconfigurations.",
        "probability": "low",
        "impact": "high",
        "mitigation": "Implement role-based access control and test permission boundaries explicitly.",
    },
    {
        "keyword": "MOBILE",
        "description": "Mobile app releases depend on App Store/Play Store review timelines, which can delay launch.",
        "probability": "medium",
        "impact": "medium",
        "mitigation": "Submit for store review early and account for review time (typically 1-2 weeks) in the launch schedule.",
    },
    {
        "keyword": "SEARCH",
        "description": "Search functionality quality and performance can be harder to get right than expected.",
        "probability": "low",
        "impact": "medium",
        "mitigation": "Start with a simple, well-tested search library before considering custom indexing infrastructure.",
    },
]

GENERIC_RISKS = [
    {
        "description": "Requirements may evolve during development as stakeholders see working software.",
        "probability": "medium",
        "impact": "medium",
        "mitigation": "Use short iteration cycles and confirm scope with stakeholders at each milestone.",
    },
]


def get_integration_risk(integration_count: int):
    if integration_count >= 3:
        return {
            "description": f"This project depends on {integration_count} external integrations, increasing the risk of third-party outages or API changes affecting delivery.",
            "probability": "medium",
            "impact": "medium",
            "mitigation": "Add fallback handling and monitoring for each third-party integration; avoid tightly coupling core flows to a single provider.",
        }
    return None


def get_scale_risk(scale_answer: str):
    if scale_answer and any(k in scale_answer.lower() for k in ["million", "thousand"]):
        return {
            "description": "The expected user scale suggests the system will need to handle significant concurrent load.",
            "probability": "medium",
            "impact": "high",
            "mitigation": "Design for horizontal scaling from the start and load-test key endpoints before launch.",
        }
    return None


def get_complexity_risk(complexity_score: float):
    if complexity_score >= 70:
        return {
            "description": "Overall project complexity is high, which increases the risk of schedule and budget overruns.",
            "probability": "medium",
            "impact": "high",
            "mitigation": "Break the project into smaller milestones and re-estimate after each phase using real progress data.",
        }
    return None