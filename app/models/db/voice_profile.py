import uuid

from sqlalchemy import (JSON, UUID, Column, DateTime, Integer, String,
                        UniqueConstraint, func)

from app.configs.database import Base


class VoiceProfileDB(Base):
    """Voice profile database model."""

    __tablename__ = "voice_profiles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    brand_id = Column(UUID(as_uuid=True), nullable=False)
    version = Column(Integer, nullable=False)
    metrics = Column(JSON, nullable=False)
    target_demographic = Column(String, nullable=False)
    style_guide = Column(JSON, nullable=False)
    writing_example = Column(String, nullable=False)
    llm_model = Column(String, nullable=False)
    source = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Unique constraint to ensure version is unique per brand
    __table_args__ = (
        UniqueConstraint("brand_id", "version", name="uq_voice_profile_brand_version"),
    )


class VoiceEvaluationDB(Base):
    """Voice evaluation database model."""

    __tablename__ = "voice_evaluations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    brand_id = Column(UUID(as_uuid=True), nullable=False)
    voice_profile_id = Column(UUID(as_uuid=True), nullable=False)
    input_text = Column(String, nullable=False)
    scores = Column(JSON, nullable=False)
    suggestions = Column(JSON, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
