"""Simplified integration tests for Voice API."""

import pytest
from fastapi import status
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from app.app import create_app
from app.configs.settings import settings


@pytest.fixture(scope="function")
def simple_client():
    """Create a simple test client without database for basic API tests."""
    app = create_app()
    
    # Force StubLLM usage
    original_stub_value = settings.USE_STUB_LLM
    settings.USE_STUB_LLM = True
    
    with TestClient(app) as test_client:
        yield test_client
    
    settings.USE_STUB_LLM = original_stub_value


class TestAPIIntegration:
    """Simplified integration tests focusing on API layer."""

    def test_root_endpoint(self, simple_client):
        """Test root endpoint returns welcome message."""
        # WHAT: Test the root API endpoint
        # WHY: Validates basic API availability
        response = simple_client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Voice API" in data["message"]
        assert "version" in data

    @patch('app.services.brand_service.BrandService.create_brand')
    def test_create_brand_api_endpoint(self, mock_create, simple_client):
        """Test brand creation API endpoint."""
        # WHAT: Test POST /brands/ endpoint with mocked service
        # WHY: Validates API request handling and response format
        from app.models.brand import Brand
        from datetime import datetime
        from uuid import uuid4
        
        mock_brand = Brand(
            id=str(uuid4()),
            name="Test Brand",
            canonical_url="https://test.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_create.return_value = mock_brand
        
        payload = {"name": "Test Brand", "canonical_url": "https://test.com"}
        response = simple_client.post("/brands/", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["brand"]["name"] == "Test Brand"

    @patch('app.services.brand_service.BrandService.get_all_brands')
    def test_get_all_brands_api_endpoint(self, mock_get_all, simple_client):
        """Test get all brands API endpoint."""
        # WHAT: Test GET /brands/ endpoint
        # WHY: Validates brand listing API functionality
        mock_get_all.return_value = []
        
        response = simple_client.get("/brands/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "brands" in data

    @patch('app.services.brand_service.BrandService.get_brand_by_id')
    def test_get_brand_by_id_not_found(self, mock_get_by_id, simple_client):
        """Test getting non-existent brand returns 404."""
        # WHAT: Test GET /brands/{id} with invalid ID
        # WHY: Validates API error handling
        mock_get_by_id.return_value = None
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = simple_client.get(f"/brands/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_brand_validation_error(self, simple_client):
        """Test brand creation with invalid payload."""
        # WHAT: Test POST /brands/ with missing required fields
        # WHY: Validates request validation
        payload = {"name": "Test Brand"}  # Missing canonical_url
        
        response = simple_client.post("/brands/", json=payload)
        
        assert response.status_code == 422  # Unprocessable Entity

    @patch('app.services.voice_service.VoiceService.generate_voice_profile')
    @patch('app.services.voice_service.fetch_page_text')
    def test_generate_voice_profile_api(self, mock_fetch, mock_generate, simple_client):
        """Test voice profile generation API endpoint."""
        # WHAT: Test POST /brands/{id}/voices:generate endpoint
        # WHY: Validates voice generation API with StubLLM
        from app.models.voice import VoiceProfile, VoiceSource
        from datetime import datetime
        from uuid import uuid4
        
        brand_id = str(uuid4())
        mock_fetch.return_value = "Content"
        mock_voice = VoiceProfile(
            id=uuid4(),
            brand_id=brand_id,
            version=1,
            metrics={"warmth": 0.5, "seriousness": 0.5, "technicality": 0.5, "formality": 0.5, "playfulness": 0.5},
            target_demographic="Test",
            style_guide=["Test"],
            writing_example="Test",
            llm_model="stub-llm",
            source=VoiceSource.MANUAL,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_generate.return_value = mock_voice
        
        payload = {
            "inputs": {"writing_samples": ["Sample"]},
            "llm_model": "stub-llm"
        }
        
        response = simple_client.post(f"/brands/{brand_id}/voices:generate", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "voice_profile" in data

    @patch('app.services.voice_service.VoiceService.get_latest_voice_profile')
    def test_get_latest_voice_profile_not_found(self, mock_get_latest, simple_client):
        """Test getting latest voice when none exists."""
        # WHAT: Test GET /brands/{id}/voices/latest with no profiles
        # WHY: Validates error handling for missing voice profiles
        mock_get_latest.side_effect = ValueError("No voice profile found")
        
        brand_id = "00000000-0000-0000-0000-000000000000"
        response = simple_client.get(f"/brands/{brand_id}/voices/latest")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('app.services.voice_service.VoiceService.get_voice_profile_by_version')
    def test_get_voice_version_not_found(self, mock_get_version, simple_client):
        """Test getting non-existent voice version."""
        # WHAT: Test GET /brands/{id}/voices/{version} with invalid version
        # WHY: Validates version-specific error handling
        mock_get_version.side_effect = ValueError("No voice profile found")
        
        brand_id = "00000000-0000-0000-0000-000000000000"
        response = simple_client.get(f"/brands/{brand_id}/voices/99")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('app.services.voice_service.VoiceService.evaluate_text')
    @patch('app.services.voice_service.VoiceService.get_voice_profile_by_version')
    @patch('app.services.voice_service.VoiceService.add_voice_evaluation')
    def test_evaluate_text_api(self, mock_add_eval, mock_get_voice, mock_evaluate, simple_client):
        """Test text evaluation API endpoint."""
        # WHAT: Test POST /brands/{id}/voices/{version}/evaluate endpoint
        # WHY: Validates evaluation API with StubLLM integration
        from app.models.voice import VoiceProfile, VoiceEvaluation, VoiceSource
        from datetime import datetime
        from uuid import uuid4
        
        brand_id = str(uuid4())
        voice_id = uuid4()
        
        mock_voice = VoiceProfile(
            id=voice_id,
            brand_id=brand_id,
            version=1,
            metrics={"warmth": 0.5, "seriousness": 0.5, "technicality": 0.5, "formality": 0.5, "playfulness": 0.5},
            target_demographic="Test",
            style_guide=["Test"],
            writing_example="Test",
            llm_model="stub-llm",
            source=VoiceSource.MANUAL,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_eval = VoiceEvaluation(
            id=uuid4(),
            brand_id=brand_id,
            voice_profile_id=voice_id,
            input_text="Test",
            scores={"warmth": 0.6, "seriousness": 0.4, "technicality": 0.5, "formality": 0.5, "playfulness": 0.3},
            suggestions=["Test suggestion"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_get_voice.return_value = mock_voice
        mock_evaluate.return_value = mock_eval
        mock_add_eval.return_value = mock_eval
        
        payload = {"text": "Test evaluation"}
        response = simple_client.post(f"/brands/{brand_id}/voices/1/evaluate", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "voice_evaluation" in data

    @patch('app.services.voice_service.VoiceService.get_voice_profile_by_version')
    def test_evaluate_with_invalid_version(self, mock_get_voice, simple_client):
        """Test evaluation with non-existent voice version."""
        # WHAT: Test evaluation against invalid voice version
        # WHY: Validates error handling in evaluation flow
        mock_get_voice.side_effect = ValueError("No voice profile found")
        
        brand_id = "00000000-0000-0000-0000-000000000000"
        payload = {"text": "Test"}
        response = simple_client.post(f"/brands/{brand_id}/voices/99/evaluate", json=payload)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_stub_llm_deterministic_behavior(self):
        """Test that StubLLM produces deterministic results."""
        # WHAT: Verify StubLLM consistency
        # WHY: Validates deterministic test environment
        from app.llm.stub import StubLLM
        
        stub_llm = StubLLM()
        
        score1 = stub_llm._deterministic_score("test")
        score2 = stub_llm._deterministic_score("test")
        
        assert score1 == score2
        assert 0.0 <= score1 <= 1.0

    def test_stub_llm_voice_profile_generation(self):
        """Test StubLLM voice profile generation."""
        # WHAT: Test StubLLM generates valid voice profiles
        # WHY: Validates StubLLM integration for testing
        from app.llm.stub import StubLLM
        from app.models.brand import Brand
        from datetime import datetime
        from uuid import uuid4
        
        stub_llm = StubLLM()
        brand = Brand(
            id=str(uuid4()),
            name="Test Brand",
            canonical_url="https://test.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        voice_profile = stub_llm.generate_voice_profile(
            brand=brand,
            site_text="Test content",
            samples=["Sample 1"]
        )
        
        assert str(voice_profile.brand_id) == brand.id
        assert len(voice_profile.metrics) == 5
        assert all(0.0 <= score <= 1.0 for score in voice_profile.metrics.values())

    def test_stub_llm_text_evaluation(self):
        """Test StubLLM text evaluation."""
        # WHAT: Test StubLLM evaluates text correctly
        # WHY: Validates evaluation logic for testing
        from app.llm.stub import StubLLM
        from app.models.voice import VoiceProfile, VoiceSource
        from datetime import datetime
        from uuid import uuid4
        
        stub_llm = StubLLM()
        voice_profile = VoiceProfile(
            id=uuid4(),
            brand_id=str(uuid4()),
            version=1,
            metrics={"warmth": 0.7, "seriousness": 0.6, "technicality": 0.5, "formality": 0.7, "playfulness": 0.4},
            target_demographic="Test",
            style_guide=["Test"],
            writing_example="Test",
            llm_model="stub-llm",
            source=VoiceSource.MANUAL,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        evaluation = stub_llm.evaluate_text(voice_profile=voice_profile, text="Test text")
        
        assert evaluation.input_text == "Test text"
        assert len(evaluation.scores) == 5
        assert len(evaluation.suggestions) > 0
