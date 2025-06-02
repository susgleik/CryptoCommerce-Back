from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Any
from ...database.database import get_db
from ...models.user_model import User, UserProfile
from ...schemas.user_schemas import UserCreate, UserResponse, UserLogin, Token, PaginatedUserResponse, UserProfileCreate
from ...auth.dependencies import get_current_user, get_current_admin
from ...auth.jwt_handler import create_access_token, get_password_hash, verify_password
from datetime import datetime, timedelta
import os
from jose import JWTError, jwt

router = APIRouter()

SECRET_KEY = "tu_clave_secreta_muy_segura"
ALGORITHM = "HS256"

def validate_token_and_get_user(token: str, db: Session) -> User:
    """
    Función auxiliar para validar el token y obtener el usuario
    """
    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user email"
            )
        
        # Buscar usuario en la base de datos
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

@router.get(
    "/users",
    response_model=PaginatedUserResponse,
    description="Get a paginated list of users - Token required as parameter",
    tags=["Users"],
    summary="List Users (Token as Parameter)"
)
async def get_users(
    token: str = Query(..., description="JWT access token obtained from login"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    items_per_page: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista paginada de usuarios.
    
    **Parámetros requeridos:**
    - **token**: El access_token que obtuviste del login
    - **page**: Número de página (opcional, default: 1)
    - **items_per_page**: Elementos por página (opcional, default: 10)
    
    **Ejemplo de uso:**
    ```
    GET /users?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&page=1&items_per_page=10
    ```
    
    **Solo usuarios admin pueden acceder a este endpoint**
    """
    
    # Validar token y obtener usuario
    current_user = validate_token_and_get_user(token, db)
    
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