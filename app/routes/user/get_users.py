from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Any, Annotated
from ...database.database import get_db
from ...models.user_model import User, UserProfile
from ...schemas.user_schemas import UserCreate, UserResponse, UserLogin, Token, PaginatedUserResponse, UserProfileCreate
from ...auth.dependencies import get_current_user, get_current_admin, validate_token_and_get_user
from ...auth.jwt_handler import create_access_token, get_password_hash, verify_password
from datetime import datetime, timedelta
import os
from jose import JWTError, jwt

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/users",
    response_model=PaginatedUserResponse,
    description="Get a paginated list of users - Admin access required",
    tags=["Users"],
    summary="List Users"
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    items_per_page: int = Query(10, ge=1, le=100, description="Number of items per page"),
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
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
    
    # Debug: Imprimir información del token
    print(f"Token received: {credentials.credentials[:20]}...")
    
    # Validar token y obtener usuario
    current_user = validate_token_and_get_user(credentials, db)
    
    print(f"User authenticated: {current_user.email}, type: {current_user.user_type}")
    
    # Verificar si es administrador
    if current_user.user_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required"
        )
    
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