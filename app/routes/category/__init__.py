from fastapi import APIRouter

from .category_post import router as category_post

# main router for category-related endpoints
router = APIRouter()

# Include all category routers
router.include_router(category_post)

# Metadata
__version__ = "1.0.0"
__description__ = "Category management endpoints for the e-commerce API"

# Export the router
__all__ = ["router"]