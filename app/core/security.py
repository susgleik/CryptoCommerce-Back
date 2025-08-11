from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from ..database.database import get_db
from ..models.user_model import User
from typing import Optional
from datetime import datetime
from app.config import settings
import app.services.auth_service as auth_service

security = HTTPBearer(auto_error=False, description="Bearer token authentication")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Obtiene el usuario actual basado en el token Bearer.
    Permite usar el token directamente en el header Authorization.
    """
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependencia para obtener usuario activo"""
    # Aquí podrías agregar validaciones adicionales como:
    # - Usuario bloqueado
    # - Usuario verificado
    # - etc.
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verifica que el usuario actual tenga privilegios de administrador.
    """ 
    if current_user.user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
    

