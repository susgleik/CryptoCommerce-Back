from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from ...database.database import get_db
from ...models.user_model import User
from ...schemas.user_schemas import PaginatedUserResponse
from ...core.dependencies import get_current_admin_user

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedUserResponse,
    description="Get a paginated list of users - Admin access required",
    tags=["Users"],
    summary="List Users"
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    items_per_page: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Obtiene una lista paginada de usuarios.

    **Autenticación requerida:**
    - **Bearer Token**: Click en "Authorize" para ingresar tu token

    **Parámetros opcionales:**
    - **page**: Número de página (default: 1)
    - **items_per_page**: Elementos por página (default: 10)

    **Pasos para usar en FastAPI Docs:**
    1. Haz login en /auth/login para obtener el access_token
    2. Click en el botón "Authorize" (🔒) en la parte superior
    3. Ingresa tu token (sin "Bearer ", solo el token)
    4. Click "Authorize"
    5. Ahora puedes usar este endpoint

    **Solo usuarios admin pueden acceder a este endpoint**
    """

    # Lógica de paginación
    skip = (page - 1) * items_per_page

    # Obtener total de usuarios
    total = db.query(User).count()

    # Obtener usuarios paginados
    users = db.query(User).offset(skip).limit(items_per_page).all()

    return {
        "items": users,
        "total": total,
        "page": page,
        "items_per_page": items_per_page,
        "total_pages": (total + items_per_page - 1) // items_per_page,
        "current_user": {
            "username": current_user.username,
            "user_type": current_user.user_type
        }
    }