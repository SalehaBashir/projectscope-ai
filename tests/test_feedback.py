from pydantic import ValidationError

import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "backend")
)

from app.schemas.feedback import FeedbackCreate, FeedbackSummary


def test_valid_feedback_create():
    data = FeedbackCreate(
        actual_hours=40.0,
        estimated_hours=50.0,
        notes="Slightly overestimated",
    )
    assert data.actual_hours == 40.0
    assert data.estimated_hours == 50.0
    assert data.task_id is None


def test_feedback_requires_actual_hours():
    try:
        FeedbackCreate()
        assert False, "should have raised"
    except ValidationError:
        pass


def test_feedback_rejects_negative_actual_hours():
    try:
        FeedbackCreate(actual_hours=-5)
        assert False, "should have raised"
    except ValidationError:
        pass


def test_feedback_rejects_negative_estimated_hours():
    try:
        FeedbackCreate(actual_hours=10, estimated_hours=-1)
        assert False, "should have raised"
    except ValidationError:
        pass


def test_feedback_summary_defaults():
    summary = FeedbackSummary(
        project_id="00000000-0000-0000-0000-000000000001",
        total_feedback_count=0,
        total_actual_hours=0.0,
    )
    assert summary.total_estimated_hours is None
    assert summary.average_deviation_percent is None
