import uuid

from sqlalchemy import UUID, Column, DateTime, String, func

from app.configs.database import Base


class BrandDB(Base):
    """Complete brand information."""

    __tablename__ = "brands"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    name = Column(String, index=True, nullable=False)
    canonical_url = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
