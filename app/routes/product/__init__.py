from fastapi import APIRouter

from .product_post import router as product_post

# main router for product-related endpoints
router = APIRouter()

router.include_router(product_post)


# Metadata
__version__ = "1.0.0"
__description__ = "Product management endpoints for the e-commerce API"

# Export the router
__all__ = ["router"]