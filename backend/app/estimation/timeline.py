from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.task import Task


DEFAULT_START_DATE = datetime.now()
WORKING_HOURS_PER_DAY = 6


def calculate_task_schedule(
    db: Session,
    tasks: list[Task],
    start_date: datetime = DEFAULT_START_DATE,
):
    """
    Build a dependency-aware project schedule.

    - Tasks without dependencies can run in parallel.
    - Dependent tasks start after their dependency finishes.
    - Task duration is calculated from available working hours.
    - Circular dependencies are rejected.
    """

    task_map = {task.id: task for task in tasks}
    scheduled = {}
    visiting = set()

    def schedule_task(task: Task):
        if task.id in scheduled:
            return scheduled[task.id]

        if task.id in visiting:
            raise ValueError("Circular task dependency detected")

        visiting.add(task.id)

        # A task with a dependency starts after that dependency finishes.
        if task.depends_on:
            dependency = task_map.get(task.depends_on)

            if dependency is None:
                raise ValueError(
                    f"Dependency task {task.depends_on} not found"
                )

            dependency_schedule = schedule_task(dependency)
            task_start = dependency_schedule["end_date"]
        else:
            # Independent tasks can start at the same time.
            task_start = start_date

        hours = max(float(task.base_hours or 0), 0.0)

        # Convert effort hours into working days.
        duration_days = max(
            hours / WORKING_HOURS_PER_DAY,
            1.0,
        )

        task_end = task_start + timedelta(days=duration_days)

        result = {
            "task_id": task.id,
            "start_date": task_start,
            "end_date": task_end,
            "duration_days": round(duration_days, 2),
        }

        scheduled[task.id] = result
        visiting.remove(task.id)

        return result

    for task in tasks:
        schedule_task(task)

    return list(scheduled.values())


def calculate_project_timeline(
    tasks: list[Task],
    schedule: list[dict],
    start_date: datetime = DEFAULT_START_DATE,
):
    """
    Calculate the overall project timeline from the scheduled tasks.

    The project duration is based on the longest dependency chain / latest
    task completion rather than simply dividing total hours by weekly capacity.
    """

    if not tasks or not schedule:
        return {
            "start_date": start_date,
            "end_date": start_date,
            "duration_days": 0.0,
            "timeline_weeks": 0.0,
        }

    start_dates = [
        item["start_date"]
        for item in schedule
        if item.get("start_date") is not None
    ]

    end_dates = [
        item["end_date"]
        for item in schedule
        if item.get("end_date") is not None
    ]

    project_start = min(start_dates) if start_dates else start_date
    project_end = max(end_dates) if end_dates else project_start

    duration_days = max(
        (project_end - project_start).total_seconds() / 86400,
        0.0,
    )

    timeline_weeks = duration_days / 7

    return {
        "start_date": project_start,
        "end_date": project_end,
        "duration_days": round(duration_days, 2),
        "timeline_weeks": round(timeline_weeks, 2),
    }