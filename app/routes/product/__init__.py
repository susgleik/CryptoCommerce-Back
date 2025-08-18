from fastapi import APIRouter

from .product_post import router as product_post
from .product_gets import router as product_gets
from .product_puts import router as product_puts
from .product_patchs import router as product_patchs
from .product_deletes import router as product_deletes

# main router for product-related endpoints
router = APIRouter()

router.include_router(product_post)
router.include_router(product_gets)
router.include_router(product_puts)
router.include_router(product_patchs)
router.include_router(product_deletes)


# Metadata
__version__ = "1.0.0"
__description__ = "Product management endpoints for the e-commerce API"

# Export the router
__all__ = ["router"]