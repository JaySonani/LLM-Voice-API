# routers/voices.py
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.configs.database import get_db
from app.models.db.voice_profile import VoiceEvaluationDB
from app.models.voice import (CreateVoiceProfileRequest,
                              VoiceEvaluationRequest, VoiceEvaluationResponse,
                              VoiceProfileResponse)
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/{brand_id}/voices")


def get_voice_service(db: Session = Depends(get_db)) -> VoiceService:
    """Get VoiceService instance with database dependency."""
    return VoiceService(db)


@router.post(":generate", response_model=VoiceProfileResponse, status_code=201)
def generate_voice(
    brand_id: UUID,
    voice_profile_request: CreateVoiceProfileRequest,
    voice_service: VoiceService = Depends(get_voice_service),
) -> VoiceProfileResponse:
    """Generate a new voice profile version for a brand."""
    try:
        voice_profile = voice_service.generate_voice_profile(
            str(brand_id), voice_profile_request
        )

        return VoiceProfileResponse(
            success=True,
            voice_profile=voice_profile,
            message=f"Voice profile version {voice_profile.version} created successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/latest", response_model=VoiceProfileResponse)
def get_latest_voice(
    brand_id: UUID,
    voice_service: VoiceService = Depends(get_voice_service),
) -> VoiceProfileResponse:
    """Get the latest voice profile for a brand."""

    try:
        voice_profile = voice_service.get_latest_voice_profile(str(brand_id))
        return VoiceProfileResponse(
            success=True,
            voice_profile=voice_profile,
            message="Latest voice profile retrieved successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{version}", response_model=VoiceProfileResponse)
def get_voice_version(
    brand_id: UUID,
    version: int,
    voice_service: VoiceService = Depends(get_voice_service),
) -> VoiceProfileResponse:
    """Get a specific version of voice profile for a brand."""
    try:
        voice_profile = voice_service.get_voice_profile_by_version(
            str(brand_id), version
        )
        return VoiceProfileResponse(
            success=True,
            voice_profile=voice_profile,
            message=f"Voice profile version {version} retrieved successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{version}/evaluate", response_model=VoiceEvaluationResponse, status_code=201
)
def evaluate_voice(
    brand_id: UUID,
    version: int,
    voice_evaluation_request: VoiceEvaluationRequest,
    voice_service: VoiceService = Depends(get_voice_service),
) -> VoiceEvaluationResponse:
    """Evaluate text against a specific voice profile version."""

    try:
        voice_profile = voice_service.get_voice_profile_by_version(
            str(brand_id), version
        )

        evaluation = voice_service.evaluate_text(
            voice_profile, voice_evaluation_request.text
        )

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

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
