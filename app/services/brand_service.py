from typing import List

from sqlalchemy.orm import Session

from app.models.brand import Brand, CreateBrandRequest
from app.models.db.brand import BrandDB


class BrandService:
    """Service class for brand-related operations."""

    def __init__(self, db: Session):
        """Initialize BrandService with database session."""
        self.db = db

    def create_brand(self, brand: CreateBrandRequest) -> Brand:
        """Create a new brand."""
        try:
            db_brand = BrandDB(name=brand.name, canonical_url=brand.canonical_url)

            self.db.add(db_brand)
            self.db.commit()
            self.db.refresh(db_brand)

            # Convert BrandDB to Brand
            return Brand(
                id=str(db_brand.id),
                name=db_brand.name,
                canonical_url=db_brand.canonical_url,
                created_at=db_brand.created_at,
                updated_at=db_brand.updated_at,
            )
        except Exception as e:
            self.db.rollback()
            raise e

    def get_all_brands(self) -> List[Brand]:
        """Get all brands."""
        db_brands = self.db.query(BrandDB).all()

        # Convert BrandDB objects to Brand objects
        return [
            Brand(
                id=str(db_brand.id),
                name=db_brand.name,
                canonical_url=db_brand.canonical_url,
                created_at=db_brand.created_at,
                updated_at=db_brand.updated_at,
            )
            for db_brand in db_brands
        ]

    def get_brand_by_id(self, brand_id: str) -> Brand | None:
        """Get a brand by ID."""
        db_brand = self.db.query(BrandDB).filter(BrandDB.id == brand_id).first()

        if db_brand is None:
            return None

        return Brand(
            id=str(db_brand.id),
            name=db_brand.name,
            canonical_url=db_brand.canonical_url,
            created_at=db_brand.created_at,
            updated_at=db_brand.updated_at,
        )
