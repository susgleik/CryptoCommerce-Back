from fastapi import APIRouter

from .category_post import router as category_post
from .category_gets import router as category_gets
from .category_puts import router as category_puts
from .category_patchs import router as category_patchs
from .category_deletes import router as category_deletes

# main router for category-related endpoints
router = APIRouter()

# Include all category routers
router.include_router(category_post)
router.include_router(category_gets)
router.include_router(category_puts)
router.include_router(category_patchs)
router.include_router(category_deletes)



# Metadata
__version__ = "1.0.0"
__description__ = "Category management endpoints for the e-commerce API"

# Export the router
__all__ = ["router"]