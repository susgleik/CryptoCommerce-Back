"""
principal module for routes
this module is used to import all the routes
"""

from fastapi import APIRouter

from .product import router as product_router

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(
    product_router, 
    prefix="/products",
    tags=["Products"]
    )   

__all__ = [
    "product_router",
    ]

#metada for the module 
__version__ = "1.0.0"
__description__ = "Main router for the application, includes all sub-routers."