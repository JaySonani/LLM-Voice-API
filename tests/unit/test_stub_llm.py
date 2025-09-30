"""Unit tests for StubLLM implementation."""

import pytest
from datetime import datetime
from uuid import uuid4

from app.llm.stub import StubLLM
from app.models.brand import Brand
from app.models.voice import VoiceSource


class TestStubLLM:
    """Test suite for StubLLM."""

    def test_deterministic_score_returns_consistent_values(self):
        """Test that _deterministic_score returns the same score for the same seed."""
        # WHAT: Testing deterministic score generation
        # WHY: Ensures reproducibility for testing purposes
        stub_llm = StubLLM()
        seed = "test_seed"
        
        score1 = stub_llm._deterministic_score(seed)
        score2 = stub_llm._deterministic_score(seed)
        
        assert score1 == score2
        assert 0.0 <= score1 <= 1.0

    def test_deterministic_score_different_seeds_different_scores(self):
        """Test that different seeds produce different scores."""
        # WHAT: Testing score variation with different seeds
        # WHY: Ensures the hash function creates diverse scores for different inputs
        stub_llm = StubLLM()
        
        score1 = stub_llm._deterministic_score("seed1")
        score2 = stub_llm._deterministic_score("seed2")
        
        assert score1 != score2

    def test_generate_voice_profile_with_site_text_only(self):
        """Test voice profile generation with only site text."""
        # WHAT: Generate voice profile using only website content
        # WHY: Validates SITE source type and proper metric generation
        stub_llm = StubLLM()
        brand = Brand(
            id=str(uuid4()),
            name="Test Brand",
            canonical_url="https://test.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        voice_profile = stub_llm.generate_voice_profile(
            brand=brand, site_text="Sample site content", samples=None
        )
        
        assert voice_profile.source == VoiceSource.SITE
        assert str(voice_profile.brand_id) == brand.id
        assert len(voice_profile.metrics) == 5
        assert all(0.0 <= score <= 1.0 for score in voice_profile.metrics.values())

    def test_generate_voice_profile_with_samples_only(self):
        """Test voice profile generation with only writing samples."""
        # WHAT: Generate voice profile using only writing samples
        # WHY: Validates MANUAL source type and handles samples-only input
        stub_llm = StubLLM()
        brand = Brand(
            id=str(uuid4()),
            name="Test Brand",
            canonical_url="https://test.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        voice_profile = stub_llm.generate_voice_profile(
            brand=brand, site_text=None, samples=["Sample 1", "Sample 2"]
        )
        
        assert voice_profile.source == VoiceSource.MANUAL
        assert str(voice_profile.brand_id) == brand.id
        assert "Test Brand" in voice_profile.target_demographic

    def test_generate_voice_profile_with_mixed_inputs(self):
        """Test voice profile generation with both site text and samples."""
        # WHAT: Generate voice profile with both site text and writing samples
        # WHY: Validates MIXED source type for comprehensive input
        stub_llm = StubLLM()
        brand = Brand(
            id=str(uuid4()),
            name="Test Brand",
            canonical_url="https://test.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        voice_profile = stub_llm.generate_voice_profile(
            brand=brand,
            site_text="Site content",
            samples=["Sample 1", "Sample 2"]
        )
        
        assert voice_profile.source == VoiceSource.MIXED
        assert len(voice_profile.style_guide) > 0
        assert voice_profile.writing_example is not None

    def test_evaluate_text_returns_scores_and_suggestions(self, sample_voice_profile):
        """Test text evaluation returns proper scores and suggestions."""
        # WHAT: Evaluate text against a voice profile
        # WHY: Ensures evaluation produces valid scores and actionable suggestions
        stub_llm = StubLLM()
        text = "This is a test message for evaluation."
        
        evaluation = stub_llm.evaluate_text(voice_profile=sample_voice_profile, text=text)
        
        assert evaluation.brand_id == sample_voice_profile.brand_id
        assert evaluation.voice_profile_id == sample_voice_profile.id
        assert evaluation.input_text == text
        assert len(evaluation.scores) == 5
        assert all(0.0 <= score <= 1.0 for score in evaluation.scores.values())
        assert len(evaluation.suggestions) > 0

    def test_evaluate_text_deterministic_scores(self, sample_voice_profile):
        """Test that text evaluation produces deterministic scores."""
        # WHAT: Verify evaluation produces consistent scores for same input
        # WHY: Ensures reproducibility in testing environment
        stub_llm = StubLLM()
        text = "Consistent test message."
        
        evaluation1 = stub_llm.evaluate_text(voice_profile=sample_voice_profile, text=text)
        evaluation2 = stub_llm.evaluate_text(voice_profile=sample_voice_profile, text=text)
        
        assert evaluation1.scores == evaluation2.scores
