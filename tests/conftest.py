"""Pytest configuration and shared fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
from uuid import uuid4

from app.models.db.brand import BrandDB
from app.models.db.voice_profile import VoiceProfileDB, VoiceEvaluationDB
from app.configs.database import Base


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database session for testing.
    
    Note: SQLite handles UUIDs as strings, so UUID values will be stored 
    as strings in the database and comparisons will work with both UUID 
    objects and strings.
    """
    # Create in-memory SQLite database with poolclass for persistence
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_brand():
    """Create a sample brand for testing."""
    from app.models.brand import Brand
    return Brand(
        id=str(uuid4()),
        name="Test Brand",
        canonical_url="https://testbrand.com",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_voice_profile(sample_brand):
    """Create a sample voice profile for testing."""
    from app.models.voice import VoiceProfile, VoiceSource
    return VoiceProfile(
        id=uuid4(),
        brand_id=sample_brand.id,
        version=1,
        metrics={
            "warmth": 0.75,
            "seriousness": 0.60,
            "technicality": 0.45,
            "formality": 0.70,
            "playfulness": 0.55,
        },
        target_demographic="Tech-savvy professionals aged 25-40",
        style_guide=["Keep it concise", "Use active voice", "Be friendly yet professional"],
        writing_example="We're excited to help you succeed with innovative solutions.",
        llm_model="stub-llm",
        source=VoiceSource.MIXED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
