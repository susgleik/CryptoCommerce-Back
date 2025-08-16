from fastapi import APIRouter
from .get_users import router as get_users

# main router for user-related endpoints
router = APIRouter()

router.include_router(get_users)

# Metadata
__version__ = "1.0.0"
__description__ = "users management endpoints for the e-commerce API"

# Export the router
__all__ = ["router"]