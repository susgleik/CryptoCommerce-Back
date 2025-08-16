from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Any
from ...database.database import get_db
from ...models.user_model import User
from ...schemas import user_schemas
from ...core.jwt_handler import create_access_token, get_password_hash, verify_password
import bcrypt
from datetime import datetime, timezone

router = APIRouter()


# Rutas públicas (sin autenticación)
@router.post(
    "/register",
    response_model=user_schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="Registro de nuevos usuarios",
    tags=["Authentication"]
)
def register_user(
    user: user_schemas.UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    # Verificar si el email ya existe
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verificar si el username ya existe
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Crear el usuario con el tipo especificado o 'common' por defecto
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=get_password_hash(user.password),
            user_type=user.user_type,  # Usará 'common' si no se especifica
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/login",
    response_model=user_schemas.Token,
    description="Login de usuarios",
    tags=["Authentication"]
)
async def login(
    form_data: user_schemas.UserLogin,
    db: Session = Depends(get_db)
):
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == form_data.email).first()
        
        # Verificar si el usuario existe y la contraseña es correcta
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive"
            )    
            
        user.last_login = datetime.now(timezone.utc)  # Actualizar la última fecha de inicio de sesión
        print(f"User {user.email} logged in at {user.last_login}")
        try:
            db.commit() 
            db.refresh(user)
        except Exception as e:
            db.rollback()
            # Si falla la actualización, registrar pero no fallar el login
            print(f"Warning: Failed to update last_login for user {user.email}: {str(e)}")    
        
        # Crear el token de acceso
        access_token = create_access_token(data={"sub": user.email})
        
        # Retornar el token y la información del usuario
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }   
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )