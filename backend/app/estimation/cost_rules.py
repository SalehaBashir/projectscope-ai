# Cost calculation rules — Phase 10

def get_blended_rate(roles: list) -> float:
    """
    Fallback hourly rate for tasks with no assigned role (role_id is null).
    Uses the average hourly rate across all seeded roles.
    """
    if not roles:
        return 0.0
    return sum(r.hourly_rate for r in roles) / len(roles)


def get_rate_for_task(role_id, rate_by_role_id: dict, blended_rate: float) -> float:
    """
    Returns the hourly rate to use for a task:
    - the assigned role's rate if role_id is set and known
    - otherwise falls back to the blended rate
    """
    if role_id and role_id in rate_by_role_id:
        return rate_by_role_id[role_id]
    return blended_rate