"""
principal module for routes
this module is used to import all the routes
"""

from fastapi import APIRouter

from .product import router as product_router
from .auth import router as auth_router
from .user import router as user_router

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(
    user_router,
    prefix="/users",
    tags=["Users"]
)

main_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

main_router.include_router(
    product_router, 
    prefix="/products",
    tags=["Products"]
    )   

__all__ = [
    "product_router",
    "auth_router",
    ]

#metada for the module 
__version__ = "1.0.0"
__description__ = "Main router for the application, includes all sub-routers."