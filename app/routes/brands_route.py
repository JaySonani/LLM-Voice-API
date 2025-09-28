"""Brand management routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.brand import CreateBrandRequest, CreateBrandResponse, GetAllBrandsResponse
from app.services.brand_service import BrandService
from .voices_route import router as voices_router


def get_brand_service(db: Session = Depends(get_db)) -> BrandService:
    """Get BrandService instance with database dependency."""
    return BrandService(db)


# Constants
BRAND_NOT_FOUND_MSG = "Brand not found"

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("/", response_model=CreateBrandResponse)
async def create_brand(
    brand_request: CreateBrandRequest,
    brand_service: BrandService = Depends(get_brand_service),
):
    """Create a new brand with voice profile."""
    brand = brand_service.create_brand(brand_request)

    return CreateBrandResponse(
        success=True,
        brand=brand,
        message=f"Brand '{brand.name}' created successfully"
    )


@router.get("/", response_model=GetAllBrandsResponse)
async def get_all_brands(
    brand_service: BrandService = Depends(get_brand_service),
):
    """Get all brands."""
    brands = brand_service.get_all_brands()
    return GetAllBrandsResponse(
        success=True,
        brands=brands,
        message="All brands retrieved successfully"
    )


@router.get("/{brand_id}", response_model=CreateBrandResponse)
async def get_brand_by_id(
    brand_id: str,
    brand_service: BrandService = Depends(get_brand_service)
):
    """Get a brand by ID."""
    brand = brand_service.get_brand_by_id(brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail=BRAND_NOT_FOUND_MSG)

    return CreateBrandResponse(
        success=True,
        brand=brand,
        message=f"Brand '{brand.name}' retrieved successfully"
    )

# # TODO:Produces a new VoiceProfile with version = previous + 1.

router.include_router(voices_router)

# @router.post("/{brand_id}/voices/{version}/evaluate", response_model=VoiceEvaluationResponse)
# async def evaluate_voice_profile(
#     brand_id: str,
#     version: int,
#     voice_evaluation_request: VoiceEvaluationRequest,
#     # brand_service: BrandService = Depends(get_brand_service)
# ):
#     """Evaluate text against a voice profile."""

#     llm: LLMPort = StubLLM()

#     temp_voice_profile = VoiceProfile(
#         id=str(uuid4()),
#         brand_id=brand_id,
#         version=version,
#         metrics={
#             "warmth": 0.5,
#             "seriousness": 0.5,
#             "technicality": 0.5,
#             "formality": 0.5,
#             "playfulness": 0.5
#         },
#         target_demographic="",
#         style_guide=[],
#         writing_example="",
#         llm_model="",
#         source=VoiceSource.MANUAL)

#     voice_evaluation = llm.evaluate_text(
#         voice=temp_voice_profile,
#         text=voice_evaluation_request.text)

#     return VoiceEvaluationResponse(
#         success=True,
#         voice_evaluation=voice_evaluation,
#         message="Voice evaluation performed successfully"
#     )


