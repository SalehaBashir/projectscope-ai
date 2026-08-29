TASK_LIBRARY = {
    "AUTHENTICATION": [
        {"title": "Design login/signup UI", "role": "UI/UX Designer", "base_hours": 4},
        {"title": "Implement signup/login API", "role": "Backend Developer", "base_hours": 8},
        {"title": "Implement password hashing and JWT sessions", "role": "Backend Developer", "base_hours": 6},
        {"title": "Build login/signup frontend forms", "role": "Frontend Developer", "base_hours": 6},
        {"title": "Test authentication flows", "role": "QA Engineer", "base_hours": 4},
    ],
    "PAYMENT_PROCESSING": [
        {"title": "Select and configure payment provider", "role": "Backend Developer", "base_hours": 3},
        {"title": "Design checkout/payment UI states", "role": "UI/UX Designer", "base_hours": 4},
        {"title": "Integrate payment gateway API", "role": "Backend Developer", "base_hours": 10},
        {"title": "Implement webhook verification", "role": "Backend Developer", "base_hours": 5},
        {"title": "Build payment interface", "role": "Frontend Developer", "base_hours": 6},
        {"title": "Test successful/failed/refund payment scenarios", "role": "QA Engineer", "base_hours": 6},
    ],
    "ADMIN_PANEL": [
        {"title": "Design admin dashboard layout", "role": "UI/UX Designer", "base_hours": 5},
        {"title": "Build admin API endpoints", "role": "Backend Developer", "base_hours": 8},
        {"title": "Build admin dashboard frontend", "role": "Frontend Developer", "base_hours": 10},
        {"title": "Implement role-based access control", "role": "Backend Developer", "base_hours": 5},
        {"title": "Test admin permissions and edge cases", "role": "QA Engineer", "base_hours": 4},
    ],
    "REAL_TIME_NOTIFICATIONS": [
        {"title": "Set up WebSocket/real-time infrastructure", "role": "Backend Developer", "base_hours": 8},
        {"title": "Build notification UI components", "role": "Frontend Developer", "base_hours": 5},
        {"title": "Test real-time delivery under load", "role": "QA Engineer", "base_hours": 4},
    ],
    "SEARCH": [
        {"title": "Design search UI and filters", "role": "UI/UX Designer", "base_hours": 3},
        {"title": "Implement search backend/indexing", "role": "Backend Developer", "base_hours": 8},
        {"title": "Build search frontend", "role": "Frontend Developer", "base_hours": 5},
        {"title": "Test search accuracy and performance", "role": "QA Engineer", "base_hours": 3},
    ],
    "MESSAGING": [
        {"title": "Design chat/messaging UI", "role": "UI/UX Designer", "base_hours": 4},
        {"title": "Implement messaging backend", "role": "Backend Developer", "base_hours": 10},
        {"title": "Build messaging frontend", "role": "Frontend Developer", "base_hours": 8},
        {"title": "Test message delivery and edge cases", "role": "QA Engineer", "base_hours": 4},
    ],
}


DEFAULT_TASKS = [
    {"title": "Design UI for this feature", "role": "UI/UX Designer", "base_hours": 3},
    {"title": "Implement backend logic", "role": "Backend Developer", "base_hours": 6},
    {"title": "Implement frontend UI", "role": "Frontend Developer", "base_hours": 5},
    {"title": "Test this feature", "role": "QA Engineer", "base_hours": 3},
]


def get_baseline_tasks(canonical_feature_name: str) -> list:
    for key, tasks in TASK_LIBRARY.items():
        if key in canonical_feature_name:
            return tasks
    return DEFAULT_TASKS