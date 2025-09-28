
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.llm.ports import LLMPort
from app.llm.provider import ProviderLLM
from app.llm.stub import StubLLM
from app.models.brand import CreateBrandRequest, Brand
from app.models.db.brand import BrandDB
from app.models.db.voice_profile import VoiceEvaluationDB, VoiceProfileDB
from app.models.voice import CreateVoiceProfileRequest, VoiceEvaluation, VoiceProfile, VoiceProfileResponse
from app.tool import fetch_page_text


class VoiceService:
    """Service class for voice-related operations."""

    def __init__(self, db: Session):
        """Initialize VoiceService with database session."""
        self.db = db

    def generate_voice_profile(self, brand_id: str, voice_profile_request: CreateVoiceProfileRequest) -> VoiceProfileResponse:
        """Generate a voice profile for a brand with versioning."""

        brand = self.db.query(BrandDB).filter(BrandDB.id == brand_id).first()
        if brand is None:
            return VoiceProfileResponse(
                success=False,
                voice_profile=None,
                message=f"Brand with id {brand_id} not found"
            )

        # Get the latest version for this brand
        latest_voice = self.db.query(VoiceProfileDB).filter(
            VoiceProfileDB.brand_id == brand_id
        ).order_by(desc(VoiceProfileDB.version)).first()
        
        # Calculate next version number
        next_version = 1 if latest_voice is None else latest_voice.version + 1

        urls = voice_profile_request.inputs.urls or []
        writing_samples = voice_profile_request.inputs.writing_samples or []

        site_text = []
        for url in urls:
            site_text.append(fetch_page_text(url))


        llm: LLMPort = ProviderLLM(voice_profile_request.llm_model)

        # Generate voice profile with LLM
        voice_profile = llm.generate_voice_profile(
            brand=brand,
            site_text=" ".join(site_text),
            samples=writing_samples)

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
            source=voice_profile.source.value
        )

        self.db.add(voice_profile_db)
        self.db.commit()
        self.db.refresh(voice_profile_db)

        return VoiceProfileResponse(
            success=True,
            voice_profile=voice_profile,
            message=f"Voice profile version {next_version} created successfully"
        )

    def get_latest_voice_profile(self, brand_id: str) -> Optional[VoiceProfile]:
        """Get the latest voice profile for a brand."""
        voice_profile_db = self.db.query(VoiceProfileDB).filter(
            VoiceProfileDB.brand_id == brand_id
        ).order_by(desc(VoiceProfileDB.version)).first()
        
        if voice_profile_db is None:
            return None
            
        return self._db_to_pydantic(voice_profile_db)

    def get_voice_profile_by_version(self, brand_id: str, version: int) -> Optional[VoiceProfile]:
        """Get a specific version of voice profile for a brand."""
        voice_profile_db = self.db.query(VoiceProfileDB).filter(
            VoiceProfileDB.brand_id == brand_id,
            VoiceProfileDB.version == version
        ).first()
        
        if voice_profile_db is None:
            return None
            
        return self._db_to_pydantic(voice_profile_db)
    

    def add_voice_evaluation(self, voice_evaluation_db: VoiceEvaluationDB) -> VoiceEvaluation:
        """Add a voice evaluation to the database."""
        self.db.add(voice_evaluation_db)
        self.db.commit()
        self.db.refresh(voice_evaluation_db)
        return self._db_to_pydantic_evaluation(voice_evaluation_db)
    
    def evaluate_text(self, voice_profile: VoiceProfile, text: str) -> VoiceEvaluation:
        """Evaluate text against a voice profile."""
        llm: LLMPort = ProviderLLM(voice_profile.llm_model)
        return llm.evaluate_text(voice=voice_profile, text=text)


    def _db_to_pydantic(self, voice_profile_db: VoiceProfileDB) -> VoiceProfile:
        """Convert database model to Pydantic model."""
        from app.models.voice import VoiceSource
        
        return VoiceProfile(
            id=voice_profile_db.id,
            brand_id=voice_profile_db.brand_id,
            version=voice_profile_db.version,
            metrics=voice_profile_db.metrics,
            target_demographic=voice_profile_db.target_demographic,
            style_guide=voice_profile_db.style_guide,
            writing_example=voice_profile_db.writing_example,
            llm_model=voice_profile_db.llm_model,
            source=VoiceSource(voice_profile_db.source),
            created_at=voice_profile_db.created_at,
            updated_at=voice_profile_db.updated_at
        )

    def _db_to_pydantic_evaluation(self, voice_evaluation_db: VoiceEvaluationDB) -> VoiceEvaluation:
        """Convert VoiceEvaluationDB to VoiceEvaluation Pydantic model."""
        return VoiceEvaluation(
            id=voice_evaluation_db.id,
            brand_id=voice_evaluation_db.brand_id,
            voice_profile_id=voice_evaluation_db.voice_profile_id,
            input_text=voice_evaluation_db.input_text,
            scores=voice_evaluation_db.scores,
            suggestions=voice_evaluation_db.suggestions,
            created_at=voice_evaluation_db.created_at,
            updated_at=voice_evaluation_db.updated_at
        )
    


