"""Brand-related Pydantic models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Brand(BaseModel):
    """Complete brand information."""

    id: str
    name: str = Field(description="Brand name")
    canonical_url: str = Field(description="Canonical brand URL")

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CreateBrandRequest(BaseModel):
    """Request model for creating a brand."""

    name: str = Field(description="Brand name")
    canonical_url: str = Field(description="Canonical brand URL")

class CreateBrandResponse(BaseModel):
    """Response model for a brand."""

    success: bool = Field(description="Whether the operation was successful")
    brand: Brand
    message: str = Field(description="Response message")

class GetAllBrandsResponse(BaseModel):
    """Response model for all brands."""

    success: bool = Field(description="Whether the operation was successful")
    brands: List[Brand]
    message: str = Field(description="Response message")