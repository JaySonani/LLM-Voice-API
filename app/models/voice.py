"""Voice-related Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class VoiceSource(str, Enum):
    """Voice profile source enumeration."""

    SITE = "site"
    MANUAL = "manual"
    MIXED = "mixed"


class VoiceProfile(BaseModel):
    """Core voice characteristics for a brand."""

    id: UUID = Field(description="Unique voice profile identifier")
    brand_id: UUID = Field(description="Foreign key to brand")
    version: int = Field(description="Version number, unique per brand")
    metrics: Dict[str, float] = Field(
        description="Voice metrics with scores between 0-1",
        example={"warmth": 0.7, "seriousness": 0.5, "technicality": 0.8},
    )
    target_demographic: str = Field(description="Target audience demographic")
    style_guide: List[str] = Field(description="List of style guidelines")
    writing_example: str = Field(description="Example of writing style")
    llm_model: str = Field(description="LLM model used for generation")
    source: VoiceSource = Field(description="Source of voice profile data")

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VoiceProfileMetrics(BaseModel):
    """Voice profile metrics."""

    warmth: float = Field(description="Warmth score")
    seriousness: float = Field(description="Seriousness score")
    technicality: float = Field(description="Technicality score")
    formality: float = Field(description="Formality score")
    playfulness: float = Field(description="Playfulness score")


class VoiceEvaluation(BaseModel):
    """Voice evaluation results for a given input text."""

    id: UUID = Field(description="Unique evaluation identifier")
    brand_id: UUID = Field(description="Foreign key to brand")
    voice_profile_id: Optional[UUID] = Field(
        None, description="Foreign key to voice profile"
    )
    input_text: str = Field(description="Text that was evaluated")
    scores: Dict[str, float] = Field(
        description="Evaluation scores matching voice profile metrics",
        example={"warmth": 0.6, "seriousness": 0.8, "technicality": 0.4},
    )
    suggestions: List[str] = Field(description="List of improvement suggestions")

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# HTTP API Models
class VoiceProfileInputs(BaseModel):
    """Input data for generating a voice profile."""

    urls: Optional[List[str]] = Field(
        default=None, description="List of URLs to analyze"
    )
    writing_samples: Optional[List[str]] = Field(
        default=None, description="List of writing samples to analyze"
    )

    @model_validator(mode="after")
    def validate_inputs(self):
        """Validate that at least one input source is provided."""
        if not self.urls and not self.writing_samples:
            raise ValueError(
                "At least one of 'urls' or 'writing_samples' must be provided"
            )
        return self


class CreateVoiceProfileRequest(BaseModel):
    """Request model for generating a voice profile."""

    inputs: VoiceProfileInputs = Field(
        description="Input data with required 'urls' and 'writing_samples' fields as string arrays"
    )
    llm_model: str = Field(description="LLM model to use for generation")

    model_config = ConfigDict(extra="forbid")


class VoiceProfileResponse(BaseModel):
    """Response model for a voice profile."""

    success: bool = Field(description="Whether the operation was successful")
    voice_profile: Optional[VoiceProfile] = Field(
        description="Voice profile data, None if operation failed"
    )
    message: str = Field(description="Response message")


class VoiceEvaluationRequest(BaseModel):
    """Request model for evaluating a text."""

    text: str = Field(description="Text to evaluate")

    model_config = ConfigDict(extra="forbid")


class VoiceEvaluationResponse(BaseModel):
    """Response model for a voice evaluation."""

    success: bool = Field(description="Whether the operation was successful")
    voice_evaluation: VoiceEvaluation
    message: str = Field(description="Response message")


# LLM Models
class VoiceProfileResponseLLM(BaseModel):
    """Response model for a voice profile from LLM."""

    metrics: VoiceProfileMetrics = Field(
        description="Voice metrics scores",
    )
    target_demographic: str = Field(description="Target audience demographic")
    style_guide: List[str] = Field(description="List of style guidelines")
    writing_example: str = Field(description="Example of writing style")


class VoiceEvaluationResponseLLM(BaseModel):
    """Response model for a voice evaluation from LLM."""

    scores: VoiceProfileMetrics = Field(
        description="Voice metrics scores",
    )
    suggestions: List[str] = Field(description="List of improvement suggestions")
