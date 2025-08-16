from fastapi import APIRouter
from .auth_users import router as auth_users_router

# main router for authentication-related endpoints
router = APIRouter()

router.include_router(auth_users_router)


# Metadata
__version__ = "1.0.0"
__description__ = "Authentication endpoints for the e-commerce API"

# Export the router
__all__ = ["router"]
