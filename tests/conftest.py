import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.config import TEST_DATABASE_URL


# =========================================================
# TEST DATABASE
# =========================================================

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# =========================================================
# CREATE TEST DATABASE TABLES
# =========================================================

@pytest.fixture(scope="function")
def db():
    """
    Create fresh database tables before each test
    and remove them after the test.
    """

    Base.metadata.create_all(bind=test_engine)

    db_session = TestingSessionLocal()

    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=test_engine)


# =========================================================
# OVERRIDE FASTAPI DATABASE
# =========================================================

@pytest.fixture(scope="function")
def client(db):
    """
    Use test database instead of real database.
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()