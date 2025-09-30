"""Unit tests for VoiceService."""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime

from app.services.voice_service import VoiceService
from app.models.voice import CreateVoiceProfileRequest, VoiceProfileInputs, VoiceSource, VoiceProfile
from app.models.db.brand import BrandDB
from app.models.db.voice_profile import VoiceProfileDB
from app.configs.settings import settings


class TestVoiceService:
    """Test suite for VoiceService."""

    def test_get_llm_instance_returns_stub_when_configured(self):
        """Test that StubLLM is returned when USE_STUB_LLM is True."""
        # WHAT: Get LLM instance with USE_STUB_LLM=True
        # WHY: Ensures correct LLM provider selection based on settings
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        # Temporarily set USE_STUB_LLM to True
        original_value = settings.USE_STUB_LLM
        settings.USE_STUB_LLM = True
        
        llm = service._get_llm_instance("stub-llm")
        
        from app.llm.stub import StubLLM
        assert isinstance(llm, StubLLM)
        
        # Restore original value
        settings.USE_STUB_LLM = original_value

    def test_generate_voice_profile_creates_first_version(self):
        """Test that first voice profile has version 1."""
        # WHAT: Generate initial voice profile for a brand
        # WHY: Validates versioning starts at 1 for new brands
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        brand_id = str(uuid4())
        brand = BrandDB(name="Test Brand", canonical_url="https://test.com")
        brand.id = brand_id
        
        # Mock database queries
        mock_brand_query = Mock()
        mock_brand_filter = Mock()
        mock_brand_filter.first.return_value = brand
        mock_brand_query.filter.return_value = mock_brand_filter
        
        mock_voice_query = Mock()
        mock_voice_filter = Mock()
        mock_voice_order = Mock()
        mock_voice_order.first.return_value = None  # No existing voice profiles
        mock_voice_filter.order_by.return_value = mock_voice_order
        mock_voice_query.filter.return_value = mock_voice_filter
        
        mock_session.query.side_effect = [mock_brand_query, mock_voice_query]
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        
        with patch('app.services.voice_service.fetch_page_text', return_value="Mocked"):
            request = CreateVoiceProfileRequest(
                inputs=VoiceProfileInputs(writing_samples=["Sample"]),
                llm_model="stub-llm"
            )
            
            original_value = settings.USE_STUB_LLM
            settings.USE_STUB_LLM = True
            
            voice_profile = service.generate_voice_profile(brand_id, request)
            
            settings.USE_STUB_LLM = original_value
        
        assert voice_profile.version == 1

    def test_generate_voice_profile_increments_version(self):
        """Test that subsequent voice profiles increment version."""
        # WHAT: Generate multiple voice profiles to test version increment
        # WHY: Ensures versioning system works correctly
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        brand_id = str(uuid4())
        brand = BrandDB(name="Test Brand", canonical_url="https://test.com")
        brand.id = brand_id
        
        # Existing voice profile with version 1
        existing_voice = VoiceProfileDB(
            id=uuid4(),
            brand_id=brand_id,
            version=1,
            metrics={},
            target_demographic="Test",
            style_guide=[],
            writing_example="Test",
            llm_model="stub-llm",
            source="manual"
        )
        
        # Mock queries
        mock_brand_query = Mock()
        mock_brand_filter = Mock()
        mock_brand_filter.first.return_value = brand
        mock_brand_query.filter.return_value = mock_brand_filter
        
        mock_voice_query = Mock()
        mock_voice_filter = Mock()
        mock_voice_order = Mock()
        mock_voice_order.first.return_value = existing_voice
        mock_voice_filter.order_by.return_value = mock_voice_order
        mock_voice_query.filter.return_value = mock_voice_filter
        
        mock_session.query.side_effect = [mock_brand_query, mock_voice_query]
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        
        with patch('app.services.voice_service.fetch_page_text', return_value="Mocked"):
            request = CreateVoiceProfileRequest(
                inputs=VoiceProfileInputs(writing_samples=["Sample"]),
                llm_model="stub-llm"
            )
            
            original_value = settings.USE_STUB_LLM
            settings.USE_STUB_LLM = True
            
            voice_profile = service.generate_voice_profile(brand_id, request)
            
            settings.USE_STUB_LLM = original_value
        
        assert voice_profile.version == 2

    def test_generate_voice_profile_with_urls(self):
        """Test voice profile generation with URLs."""
        # WHAT: Generate voice profile from website URLs
        # WHY: Validates URL-based voice profiling
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        brand_id = str(uuid4())
        brand = BrandDB(name="Test Brand", canonical_url="https://test.com")
        brand.id = brand_id
        
        # Mock queries
        mock_brand_query = Mock()
        mock_brand_filter = Mock()
        mock_brand_filter.first.return_value = brand
        mock_brand_query.filter.return_value = mock_brand_filter
        
        mock_voice_query = Mock()
        mock_voice_filter = Mock()
        mock_voice_order = Mock()
        mock_voice_order.first.return_value = None
        mock_voice_filter.order_by.return_value = mock_voice_order
        mock_voice_query.filter.return_value = mock_voice_filter
        
        mock_session.query.side_effect = [mock_brand_query, mock_voice_query]
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        
        with patch('app.services.voice_service.fetch_page_text', return_value="Mocked content"):
            request = CreateVoiceProfileRequest(
                inputs=VoiceProfileInputs(urls=["https://test.com/page1"]),
                llm_model="stub-llm"
            )
            
            original_value = settings.USE_STUB_LLM
            settings.USE_STUB_LLM = True
            
            voice_profile = service.generate_voice_profile(brand_id, request)
            
            settings.USE_STUB_LLM = original_value
        
        assert voice_profile.source == VoiceSource.SITE

    def test_generate_voice_profile_raises_error_for_invalid_brand(self):
        """Test that error is raised for non-existent brand."""
        # WHAT: Attempt to generate voice profile for invalid brand ID
        # WHY: Validates error handling for missing brand
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        # Mock query to return None (brand not found)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        request = CreateVoiceProfileRequest(
            inputs=VoiceProfileInputs(writing_samples=["Sample"]),
            llm_model="stub-llm"
        )
        
        with pytest.raises(ValueError, match="Brand with id .* not found"):
            service.generate_voice_profile(str(uuid4()), request)

    def test_get_latest_voice_profile_success(self):
        """Test getting latest voice profile for a brand."""
        # WHAT: Retrieve the most recent voice profile version
        # WHY: Validates latest version retrieval logic
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        brand_id = str(uuid4())
        voice_profile_db = VoiceProfileDB(
            id=uuid4(),
            brand_id=brand_id,
            version=2,
            metrics={"warmth": 0.5},
            target_demographic="Test",
            style_guide=["Test"],
            writing_example="Test",
            llm_model="stub-llm",
            source="manual"
        )
        voice_profile_db.created_at = datetime.now()
        voice_profile_db.updated_at = datetime.now()
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_order = Mock()
        mock_order.first.return_value = voice_profile_db
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        voice_profile = service.get_latest_voice_profile(brand_id)
        
        assert voice_profile.version == 2

    def test_get_latest_voice_profile_raises_error_if_none(self):
        """Test error when no voice profile exists for brand."""
        # WHAT: Attempt to retrieve voice profile when none exist
        # WHY: Validates error handling for missing voice profiles
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_order = Mock()
        mock_order.first.return_value = None
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        with pytest.raises(ValueError, match="No voice profile found"):
            service.get_latest_voice_profile(str(uuid4()))

    def test_get_voice_profile_by_version_success(self):
        """Test getting specific version of voice profile."""
        # WHAT: Retrieve a specific version of voice profile
        # WHY: Validates version-specific retrieval
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        brand_id = str(uuid4())
        voice_profile_db = VoiceProfileDB(
            id=uuid4(),
            brand_id=brand_id,
            version=1,
            metrics={"warmth": 0.5},
            target_demographic="Test",
            style_guide=["Test"],
            writing_example="Test",
            llm_model="stub-llm",
            source="manual"
        )
        voice_profile_db.created_at = datetime.now()
        voice_profile_db.updated_at = datetime.now()
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = voice_profile_db
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        voice_profile = service.get_voice_profile_by_version(brand_id, 1)
        
        assert voice_profile.version == 1

    def test_get_voice_profile_by_version_raises_error_if_not_found(self):
        """Test error when specific version doesn't exist."""
        # WHAT: Attempt to retrieve non-existent version
        # WHY: Validates error handling for missing versions
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        with pytest.raises(ValueError, match="No voice profile found"):
            service.get_voice_profile_by_version(str(uuid4()), 99)

    def test_evaluate_text_success(self, sample_voice_profile):
        """Test successful text evaluation."""
        # WHAT: Evaluate text against voice profile
        # WHY: Validates text evaluation functionality
        mock_session = Mock()
        service = VoiceService(mock_session)
        
        original_value = settings.USE_STUB_LLM
        settings.USE_STUB_LLM = True
        
        evaluation = service.evaluate_text(sample_voice_profile, "Test text for evaluation")
        
        settings.USE_STUB_LLM = original_value
        
        assert evaluation.input_text == "Test text for evaluation"
        assert len(evaluation.scores) == 5
        assert len(evaluation.suggestions) > 0