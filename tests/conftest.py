import os
import sys
import uuid

# Point the app at a dedicated test database BEFORE importing app modules,
# because app.database.connection creates its engine from this env var.
os.environ["DATABASE_URL"] = (
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/projectscope_test",
    )
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
# Disable the per-IP rate limiter in tests (TestClient shares one client IP).
os.environ["DISABLE_RATE_LIMIT"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.connection import Base, engine, SessionLocal
from app.models import (  # noqa: F401  ensure all models are registered
    User,
    Project,
    Requirement,
    Feature,
    Task,
    Role,
    Estimate,
    Risk,
    TechStackRecommendation,
    ThemeSelection,
    Organization,
    Milestone,
    Prediction,
    Feedback,
    LLMRequest,
)
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create all tables in the test database
    Base.metadata.create_all(bind=engine)
    yield
    # Leave the schema in place between runs; data is cleaned per test.


@pytest.fixture(autouse=True)
def clean_tables():
    """Truncate all tables before/after every test so tests are fully isolated."""
    table_names = ", ".join(
        f'"{t.name}"' for t in Base.metadata.sorted_tables if t.name != "alembic_version"
    )
    stmt = text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
    with engine.begin() as conn:
        conn.execute(stmt)
    yield
    with engine.begin() as conn:
        conn.execute(stmt)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.rollback()
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


def make_user(
    db,
    email: str = None,
    full_name: str = "Test User",
    organization_id: uuid.UUID = None,
) -> User:
    """Create a user + an organization, and seed roles once."""
    from app.services.task_service import generate_tasks_for_project  # noqa
    from app.repositories.role_repository import seed_roles

    seed_roles(db)

    org_id = organization_id or uuid.uuid4()
    user = User(
        id=uuid.uuid4(),
        email=email or f"{uuid.uuid4().hex}@test.com",
        full_name=full_name,
        hashed_password="x",
        organization_id=org_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_org_and_user(db) -> tuple:
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Test Org", slug=uuid.uuid4().hex[:8])
    db.add(org)
    db.commit()
    user = make_user(db, organization_id=org_id)
    return org_id, user


from app.database.connection import get_db  # noqa: E402
