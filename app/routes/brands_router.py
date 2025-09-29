"""Brand management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.brand import (CreateBrandRequest, CreateBrandResponse,
                              GetAllBrandsResponse)
from app.services.brand_service import BrandService

from app.routes.voices_router import router as voices_router


def get_brand_service(db: Session = Depends(get_db)) -> BrandService:
    """Get BrandService instance with database dependency."""
    return BrandService(db)


router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("/", response_model=CreateBrandResponse, status_code=201)
async def create_brand(
    brand_request: CreateBrandRequest,
    brand_service: BrandService = Depends(get_brand_service),
) -> CreateBrandResponse:
    """Create a new brand with voice profile."""
    brand = brand_service.create_brand(brand_request)

    return CreateBrandResponse(
        success=True, brand=brand, message=f"Brand '{brand.name}' created successfully"
    )


@router.get("/", response_model=GetAllBrandsResponse)
async def get_all_brands(
    brand_service: BrandService = Depends(get_brand_service),
) -> GetAllBrandsResponse:
    """Get all brands."""
    brands = brand_service.get_all_brands()

    return GetAllBrandsResponse(
        success=True, brands=brands, message=f"All {len(brands)} brands retrieved successfully"
    )


@router.get("/{brand_id}", response_model=CreateBrandResponse)
async def get_brand_by_id(
    brand_id: str,
    brand_service: BrandService = Depends(get_brand_service),
) -> CreateBrandResponse:
    """Get a brand by ID."""
    brand = brand_service.get_brand_by_id(brand_id)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id: {brand_id} not found",
        )

    return CreateBrandResponse(
        success=True,
        brand=brand,
        message=f"Brand '{brand.name}' retrieved successfully",
    )


# Include voices router behind brand router
router.include_router(voices_router)
