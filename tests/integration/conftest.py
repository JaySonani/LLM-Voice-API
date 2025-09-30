"""Integration test fixtures and configuration."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.app import create_app
from app.configs.database import Base, get_db
from app.configs.settings import settings


# Patch UUID type for SQLite compatibility
original_uuid_init = UUID.__init__

def patched_uuid_init(self, *args, **kwargs):
    """Override UUID to use String type in SQLite."""
    kwargs['as_uuid'] = False
    original_uuid_init(self, *args, **kwargs)

UUID.__init__ = patched_uuid_init


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for integration tests."""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


# Restore original UUID init after all tests
def pytest_sessionfinish(session, exitstatus):
    """Restore original UUID implementation."""
    UUID.__init__ = original_uuid_init


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override."""
    app = create_app()
    
    # Override database dependency
    def override_get_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Force StubLLM usage for integration tests
    original_stub_value = settings.USE_STUB_LLM
    settings.USE_STUB_LLM = True
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore original setting
    settings.USE_STUB_LLM = original_stub_value
    app.dependency_overrides.clear()
