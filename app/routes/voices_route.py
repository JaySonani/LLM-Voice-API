# routers/voices.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID, uuid4

from sqlmodel import Session

from app.configs.database import get_db
from app.llm.ports import LLMPort
from app.llm.stub import StubLLM
from app.models.db.voice_profile import VoiceEvaluationDB
from app.models.voice import (
    CreateVoiceProfileRequest,
    VoiceEvaluationRequest,
    VoiceEvaluationResponse,
    VoiceProfileResponse,
)
from app.services import brand_service
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/{brand_id}/voices")


def get_voice_service(db: Session = Depends(get_db)) -> VoiceService:
    """Get VoiceService instance with database dependency."""
    return VoiceService(db)


@router.post(":generate")
def generate_voice(
    brand_id: UUID,
    voice_profile_request: CreateVoiceProfileRequest,
    voice_service: VoiceService = Depends(get_voice_service),
) -> VoiceProfileResponse:
    """Generate a new voice profile version for a brand."""
    voice_profile_response = voice_service.generate_voice_profile(
        str(brand_id), voice_profile_request
    )

    if not voice_profile_response.success:
        raise HTTPException(status_code=404, detail=voice_profile_response.message)

    return voice_profile_response


@router.get("/latest")
def get_latest_voice(
    brand_id: UUID,
    voice_service: VoiceService = Depends(get_voice_service),
):
    """Get the latest voice profile for a brand."""
    voice_profile = voice_service.get_latest_voice_profile(str(brand_id))

    if voice_profile is None:
        raise HTTPException(
            status_code=404, detail=f"No voice profile found for brand {brand_id}"
        )

    return voice_profile


@router.get("/{version}")
def get_voice_version(
    brand_id: UUID,
    version: int,
    voice_service: VoiceService = Depends(get_voice_service),
):
    """Get a specific version of voice profile for a brand."""
    voice_profile = voice_service.get_voice_profile_by_version(str(brand_id), version)

    if voice_profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Voice profile version {version} not found for this brand",
        )

    return voice_profile


@router.post("/{version}/evaluate")
def evaluate_voice(
    brand_id: UUID,
    version: int,
    voice_evaluation_request: VoiceEvaluationRequest,
    voice_service: VoiceService = Depends(get_voice_service),
):
    """Evaluate text against a specific voice profile version."""

    voice_profile = voice_service.get_voice_profile_by_version(str(brand_id), version)

    print(f"Voice profile: {voice_profile}")

    if voice_profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Voice profile version {version} not found for this brand",
        )

    evaluation = voice_service.evaluate_text(voice_profile, voice_evaluation_request.text)

    voice_evaluation_db = VoiceEvaluationDB(
        id=str(uuid4()),
        brand_id=brand_id,
        voice_profile_id=voice_profile.id,
        input_text=voice_evaluation_request.text,
        scores=evaluation.scores,
        suggestions=evaluation.suggestions,   
    )

    voice_evaluation = voice_service.add_voice_evaluation(voice_evaluation_db)

    return VoiceEvaluationResponse(
        success=True,
        voice_evaluation=voice_evaluation,
        message="Voice evaluation created successfully",
    )
