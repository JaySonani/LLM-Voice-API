"""Unit tests for Pydantic models and validation."""

import pytest
from pydantic import ValidationError

from app.models.brand import CreateBrandRequest
from app.models.voice import VoiceProfileInputs, VoiceSource


class TestModels:
    """Test suite for Pydantic models."""

    def test_voice_profile_inputs_requires_at_least_one_input(self):
        """Test that VoiceProfileInputs requires either URLs or writing samples."""
        # WHAT: Validate input requirement for voice profile creation
        # WHY: Ensures at least one data source is provided for profiling
        with pytest.raises(ValidationError, match="At least one of"):
            VoiceProfileInputs(urls=None, writing_samples=None)

    def test_voice_profile_inputs_accepts_urls_only(self):
        """Test that VoiceProfileInputs accepts only URLs."""
        # WHAT: Create inputs with URLs only
        # WHY: Validates URL-only input scenario
        inputs = VoiceProfileInputs(urls=["https://test.com"], writing_samples=None)
        
        assert inputs.urls == ["https://test.com"]
        assert inputs.writing_samples is None

    def test_voice_profile_inputs_accepts_writing_samples_only(self):
        """Test that VoiceProfileInputs accepts only writing samples."""
        # WHAT: Create inputs with writing samples only
        # WHY: Validates manual sample-only input scenario
        inputs = VoiceProfileInputs(urls=None, writing_samples=["Sample text"])
        
        assert inputs.writing_samples == ["Sample text"]
        assert inputs.urls is None

    def test_voice_profile_inputs_accepts_both(self):
        """Test that VoiceProfileInputs accepts both URLs and writing samples."""
        # WHAT: Create inputs with both data sources
        # WHY: Validates mixed input scenario
        inputs = VoiceProfileInputs(
            urls=["https://test.com"],
            writing_samples=["Sample"]
        )
        
        assert inputs.urls == ["https://test.com"]
        assert inputs.writing_samples == ["Sample"]

    def test_create_brand_request_forbids_extra_fields(self):
        """Test that CreateBrandRequest rejects extra fields."""
        # WHAT: Attempt to create brand request with unexpected fields
        # WHY: Ensures strict validation prevents API misuse
        with pytest.raises(ValidationError):
            CreateBrandRequest(
                name="Test",
                canonical_url="https://test.com",
                extra_field="not allowed"
            )

    def test_voice_source_enum_values(self):
        """Test VoiceSource enum has correct values."""
        # WHAT: Verify VoiceSource enum values
        # WHY: Ensures source types are correctly defined
        assert VoiceSource.SITE.value == "site"
        assert VoiceSource.MANUAL.value == "manual"
        assert VoiceSource.MIXED.value == "mixed"
