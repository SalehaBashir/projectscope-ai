THEME_PRESETS = [
    {
        "id": "modern_minimal",
        "name": "Modern Minimal",
        "primary_color": "#2E7D32",
        "secondary_color": "#F5F5F5",
        "font": "Inter",
        "description": "Clean, spacious, lots of white space. Good for SaaS tools and dashboards.",
        "best_for": ["saas", "internal_tool"],
    },
    {
        "id": "vibrant_marketplace",
        "name": "Vibrant Marketplace",
        "primary_color": "#FF6B35",
        "secondary_color": "#FFF3E0",
        "font": "Poppins",
        "description": "Warm, energetic colors. Good for consumer apps, food delivery, and marketplaces.",
       "best_for": ["food_delivery", "marketplace", "ecommerce", "food", "delivery", "restaurant"],
    },
    {
        "id": "corporate_professional",
        "name": "Corporate Professional",
        "primary_color": "#1A3C6E",
        "secondary_color": "#EDF1F7",
        "font": "Roboto",
        "description": "Trustworthy, formal, blue-toned. Good for fintech, healthcare, and B2B products.",
        "best_for": ["fintech", "healthcare", "booking_platform", "b2b"],
    },
    {
        "id": "playful_startup",
        "name": "Playful Startup",
        "primary_color": "#7C3AED",
        "secondary_color": "#F3E8FF",
        "font": "DM Sans",
        "description": "Bold, friendly, rounded shapes. Good for social apps and youth-oriented products.",
        "best_for": ["social_media", "internal_tool"],
    },
    {
        "id": "dark_mode_tech",
        "name": "Dark Mode Tech",
        "primary_color": "#00D9C0",
        "secondary_color": "#0A0E14",
        "font": "JetBrains Mono",
        "description": "Dark background, neon accents. Good for developer tools and technical products.",
        "best_for": ["saas", "internal_tool"],
    },
]


def get_theme_by_id(theme_id: str):
    return next((t for t in THEME_PRESETS if t["id"] == theme_id), None)


def suggest_theme_for_project_type(project_type: str):
    project_type_lower = (project_type or "").lower().replace("_", " ")
    for theme in THEME_PRESETS:
        for tag in theme["best_for"]:
            if tag.replace("_", " ") in project_type_lower:
                return theme
    return THEME_PRESETS[0]