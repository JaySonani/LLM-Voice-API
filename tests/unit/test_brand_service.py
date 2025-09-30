"""Unit tests for BrandService."""

import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.services.brand_service import BrandService
from app.models.brand import CreateBrandRequest
from app.models.db.brand import BrandDB
from datetime import datetime


class TestBrandService:
    """Test suite for BrandService."""

    def test_create_brand_success(self):
        """Test successful brand creation."""
        # WHAT: Create a new brand in the database
        # WHY: Validates core brand creation functionality
        mock_session = Mock()
        service = BrandService(mock_session)
        request = CreateBrandRequest(name="New Brand", canonical_url="https://newbrand.com")
        
        # Mock database operations
        mock_brand_db = BrandDB(name=request.name, canonical_url=request.canonical_url)
        mock_brand_db.id = uuid4()
        mock_brand_db.created_at = datetime.now()
        mock_brand_db.updated_at = datetime.now()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock(side_effect=lambda x: setattr(x, 'id', mock_brand_db.id) or setattr(x, 'created_at', mock_brand_db.created_at) or setattr(x, 'updated_at', mock_brand_db.updated_at))
        
        brand = service.create_brand(request)
        
        assert brand.name == "New Brand"
        assert brand.canonical_url == "https://newbrand.com"
        assert brand.id is not None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_brand_rollback_on_error(self):
        """Test that database rollback occurs on error."""
        # WHAT: Simulate error during brand creation to test rollback
        # WHY: Ensures transaction integrity and error handling
        mock_session = Mock()
        service = BrandService(mock_session)
        request = CreateBrandRequest(name="Test", canonical_url="https://test.com")
        
        # Simulate commit failure
        mock_session.commit.side_effect = Exception("Database error")
        mock_session.rollback = Mock()
        
        with pytest.raises(Exception):
            service.create_brand(request)
        
        mock_session.rollback.assert_called_once()

    def test_get_all_brands_empty(self):
        """Test getting all brands when database is empty."""
        # WHAT: Query all brands from empty database
        # WHY: Validates handling of empty result sets
        mock_session = Mock()
        service = BrandService(mock_session)
        
        mock_query = Mock()
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        
        brands = service.get_all_brands()
        
        assert brands == []

    def test_get_all_brands_returns_all(self):
        """Test that get_all_brands returns all created brands."""
        # WHAT: Create multiple brands and retrieve all
        # WHY: Validates bulk retrieval functionality
        mock_session = Mock()
        service = BrandService(mock_session)
        
        # Create mock brand DB objects
        brand1 = BrandDB(name="Brand 1", canonical_url="https://brand1.com")
        brand1.id = uuid4()
        brand1.created_at = datetime.now()
        brand1.updated_at = datetime.now()
        
        brand2 = BrandDB(name="Brand 2", canonical_url="https://brand2.com")
        brand2.id = uuid4()
        brand2.created_at = datetime.now()
        brand2.updated_at = datetime.now()
        
        mock_query = Mock()
        mock_query.all.return_value = [brand1, brand2]
        mock_session.query.return_value = mock_query
        
        brands = service.get_all_brands()
        
        assert len(brands) == 2
        assert brands[0].name == "Brand 1"
        assert brands[1].name == "Brand 2"

    def test_get_brand_by_id_exists(self):
        """Test getting a brand by ID when it exists."""
        # WHAT: Retrieve specific brand by ID
        # WHY: Validates single record retrieval
        mock_session = Mock()
        service = BrandService(mock_session)
        
        brand_id = str(uuid4())
        mock_brand = BrandDB(name="Find Me", canonical_url="https://findme.com")
        mock_brand.id = brand_id
        mock_brand.created_at = datetime.now()
        mock_brand.updated_at = datetime.now()
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_brand
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        brand = service.get_brand_by_id(brand_id)
        
        assert brand is not None
        assert brand.name == "Find Me"

    def test_get_brand_by_id_not_exists(self):
        """Test getting a brand by ID when it doesn't exist."""
        # WHAT: Attempt to retrieve non-existent brand
        # WHY: Validates proper handling of missing records
        mock_session = Mock()
        service = BrandService(mock_session)
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        brand = service.get_brand_by_id(str(uuid4()))
        
        assert brand is None