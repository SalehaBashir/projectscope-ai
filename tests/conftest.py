import os

import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.database.connection import Base, engine, SessionLocal, get_db
from app.main import app

os.environ["APP_ENV"] = "test"

import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Test database configuration
# ---------------------------------------------------------------------------

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/projectscope_test",
    ),
)


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Create database tables and make the test database compatible with
    the latest ProjectScope schema.

    create_all() only creates missing tables; it does not add new columns
    to existing tables. Therefore the IF NOT EXISTS ALTER statements below
    keep an existing projectscope_test database compatible with the current
    models/migrations.
    """

    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:

        # -------------------------------------------------------------------
        # Phase 21: project analysis fields
        # -------------------------------------------------------------------

        conn.execute(
            text(
                "ALTER TABLE projects "
                "ADD COLUMN IF NOT EXISTS assumptions "
                "JSONB NOT NULL DEFAULT '[]'::jsonb"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE projects "
                "ADD COLUMN IF NOT EXISTS missing_information "
                "JSONB NOT NULL DEFAULT '[]'::jsonb"
            )
        )

        # -------------------------------------------------------------------
        # Phase 6: feature dependency fields
        # -------------------------------------------------------------------

        conn.execute(
            text(
                "ALTER TABLE features "
                "ADD COLUMN IF NOT EXISTS dependencies "
                "JSONB NOT NULL DEFAULT '[]'::jsonb"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE features "
                "ADD COLUMN IF NOT EXISTS source_requirement_id UUID"
            )
        )

        # -------------------------------------------------------------------
        # Phase 2: organization_id on tenant-owned tables
        # -------------------------------------------------------------------

        conn.execute(
            text(
                "ALTER TABLE estimates "
                "ADD COLUMN IF NOT EXISTS organization_id UUID"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE requirements "
                "ADD COLUMN IF NOT EXISTS organization_id UUID"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE tasks "
                "ADD COLUMN IF NOT EXISTS organization_id UUID"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE feedback "
                "ADD COLUMN IF NOT EXISTS organization_id UUID"
            )
        )


# ---------------------------------------------------------------------------
# Test database cleanup
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_database():
    """
    Keep tests isolated by clearing test data after every test.

    This prevents fixed test emails and other tenant-owned records from
    leaking into subsequent tests.
    """

    yield

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE TABLE
                    feedback,
                    tasks,
                    features,
                    requirements,
                    estimates,
                    projects,
                    users,
                    organizations
                RESTART IDENTITY CASCADE
                """
            )
        )


# ---------------------------------------------------------------------------
# Test client
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """
    FastAPI TestClient with the database dependency overridden
    to use the test database session.
    """

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Database session fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def db():
    """
    Provide a database session for individual tests.
    """

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()