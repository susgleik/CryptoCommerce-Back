from fastapi import APIRouter
from .get_users import router as get_users
from .user_profile_get import router as user_profile_get
from .user_profile_post import router as user_profile_post
from .user_profile_put import router as user_profile_put
from .user_profile_patch import router as user_profile_patch
from .user_profile_delete import router as user_profile_delete

# main router for user-related endpoints
router = APIRouter()

# User management routes
router.include_router(get_users)

# User profile routes
router.include_router(user_profile_get)
router.include_router(user_profile_post)
router.include_router(user_profile_put)
router.include_router(user_profile_patch)
router.include_router(user_profile_delete)

# Metadata
__version__ = "2.0.0"
__description__ = "users management and profile endpoints for the e-commerce API"

# Export the router
__all__ = ["router"]