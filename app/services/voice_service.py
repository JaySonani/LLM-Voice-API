from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.configs.settings import settings
from app.llm.ports import LLMPort
from app.llm.provider import ProviderLLM
from app.llm.stub import StubLLM
from app.models.db.brand import BrandDB
from app.models.db.voice_profile import VoiceEvaluationDB, VoiceProfileDB
from app.models.voice import (CreateVoiceProfileRequest, VoiceEvaluation,
                              VoiceProfile)
from app.tools.scrapper_tool import fetch_page_text


class VoiceService:
    """Service class for voice-related operations."""

    def __init__(self, db: Session):
        """Initialize VoiceService with database session."""
        self.db = db

    def _get_llm_instance(self, llm_model: str) -> LLMPort:
        """Get the appropriate LLM instance based on environment configuration."""
        if settings.USE_STUB_LLM:
            return StubLLM()
        else:
            return ProviderLLM(llm_model)

    def generate_voice_profile(
        self, brand_id: str, voice_profile_request: CreateVoiceProfileRequest
    ) -> VoiceProfile:
        """Generate a voice profile for a brand with versioning."""

        brand = self.db.query(BrandDB).filter(BrandDB.id == brand_id).first()
        if brand is None:
            raise ValueError(f"Brand with id {brand_id} not found")

        # Get the latest version for this brand
        latest_voice = (
            self.db.query(VoiceProfileDB)
            .filter(VoiceProfileDB.brand_id == brand_id)
            .order_by(desc(VoiceProfileDB.version))
            .first()
        )

        # Calculate next version number
        next_version = 1 if latest_voice is None else latest_voice.version + 1

        urls = voice_profile_request.inputs.urls or []
        writing_samples = voice_profile_request.inputs.writing_samples or []

        site_text = []
        for url in urls:
            site_text.append(fetch_page_text(url))

        llm: LLMPort = self._get_llm_instance(voice_profile_request.llm_model)

        # Generate voice profile with LLM
        voice_profile = llm.generate_voice_profile(
            brand=brand, site_text=" ".join(site_text), samples=writing_samples
        )

        # Override the version with the calculated next version
        voice_profile.version = next_version

        # Convert to database model and save
        voice_profile_db = VoiceProfileDB(
            id=voice_profile.id,
            brand_id=voice_profile.brand_id,
            version=voice_profile.version,
            metrics=voice_profile.metrics,
            target_demographic=voice_profile.target_demographic,
            style_guide=voice_profile.style_guide,
            writing_example=voice_profile.writing_example,
            llm_model=voice_profile.llm_model,
            source=voice_profile.source.value,
        )

        self.db.add(voice_profile_db)
        self.db.commit()
        self.db.refresh(voice_profile_db)

        return voice_profile

    def get_latest_voice_profile(self, brand_id: str) -> Optional[VoiceProfile]:
        """Get the latest voice profile for a brand."""
        voice_profile_db = (
            self.db.query(VoiceProfileDB)
            .filter(VoiceProfileDB.brand_id == brand_id)
            .order_by(desc(VoiceProfileDB.version))
            .first()
        )

        if voice_profile_db is None:
            raise ValueError(f"No voice profile found with brand id {brand_id}")

        return VoiceProfile.model_validate(voice_profile_db.__dict__)

    def get_voice_profile_by_version(
        self, brand_id: str, version: int
    ) -> Optional[VoiceProfile]:
        """Get a specific version of voice profile for a brand."""
        voice_profile_db = (
            self.db.query(VoiceProfileDB)
            .filter(
                VoiceProfileDB.brand_id == brand_id, VoiceProfileDB.version == version
            )
            .first()
        )

        if voice_profile_db is None:
            raise ValueError(
                f"No voice profile found with brand id {brand_id} and version {version}"
            )

        return VoiceProfile.model_validate(voice_profile_db.__dict__)

    def add_voice_evaluation(
        self, voice_evaluation_db: VoiceEvaluationDB
    ) -> VoiceEvaluation:
        """Add a voice evaluation to the database."""
        self.db.add(voice_evaluation_db)
        self.db.commit()
        self.db.refresh(voice_evaluation_db)
        return VoiceEvaluation.model_validate(voice_evaluation_db.__dict__)

    def evaluate_text(self, voice_profile: VoiceProfile, text: str) -> VoiceEvaluation:
        """Evaluate text against a voice profile."""
        try:
            llm: LLMPort = self._get_llm_instance(voice_profile.llm_model)
            voice_evaluation = llm.evaluate_text(voice_profile=voice_profile, text=text)
            return voice_evaluation
        except Exception as e:
            raise ValueError(f"Error evaluating text: {e}")
