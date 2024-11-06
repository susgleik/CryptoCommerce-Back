from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Any
from ..database.database import get_db
from ..models.user_model import User
from ..schemas import user_schemas
from ..auth.dependencies import get_current_user, get_current_admin
from ..auth.jwt_handler import create_access_token, get_password_hash, verify_password
import bcrypt
from datetime import datetime

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
            user_type=user.user_type  # Usará 'common' si no se especifica
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

@router.get(
    "/users/me",
    response_model=user_schemas.UserResponse,
    dependencies=[Depends(get_current_user)]
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

admin_router = APIRouter(
    prefix="/api/admin/users",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin)]  # Todas las rutas aquí requieren ser admin
)

@admin_router.get("/", response_model=List[user_schemas.UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users



@router.put("/me", response_model=user_schemas.UserResponse)
async def update_user_me(
    user_update: user_schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.current_password:
        if not bcrypt.checkpw(
            user_update.current_password.encode(),
            current_user.password_hash.encode()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        
        if user_update.new_password:
            current_user.password_hash = bcrypt.hashpw(
                user_update.new_password.encode(),
                bcrypt.gensalt()
            ).decode()
    
    if user_update.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.user_id != current_user.user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    if user_update.username:
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.user_id != current_user.user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username
    
    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating user"
        )

@router.get("/list", response_model=user_schemas.PaginatedUserResponse)
async def get_users_list(
    page: int = Query(1, gt=0),
    items_per_page: int = Query(10, gt=0, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_term)) |
            (User.username.ilike(search_term))
        )
    
    total = query.count()
    skip = (page - 1) * items_per_page
    users = query.offset(skip).limit(items_per_page).all()
    
    return {
        "items": users,
        "total": total,
        "page": page,
        "items_per_page": items_per_page
    }

@router.get("/detail/{user_id}", response_model=user_schemas.UserResponse)
async def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

# El resto de endpoints relacionados con superusuarios se han removido ya que
# ahora usamos user_type en lugar de is_superuser

# ... (código anterior se mantiene igual hasta el endpoint de detail)

# Endpoints para administradores
@router.get("/", response_model=List[user_schemas.UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),  # Cambiaremos esta dependencia
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=user_schemas.UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}/toggle-type")
async def toggle_user_type(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevenir que el último admin se cambie a sí mismo a usuario común
    if user.user_id == current_user.user_id and user.user_type == 'admin':
        admin_count = db.query(User).filter(User.user_type == 'admin').count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change type of the last admin user"
            )
    
    # Cambiar tipo de usuario
    user.user_type = 'common' if user.user_type == 'admin' else 'admin'
    db.commit()
    
    return {
        "message": f"User type changed to {user.user_type} successfully"
    }

@router.get("/stats", response_model=dict)
async def get_user_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas sobre los usuarios (solo para administradores)
    """
    total_users = db.query(User).count()
    common_users = db.query(User).filter(User.user_type == 'common').count()
    admin_users = db.query(User).filter(User.user_type == 'admin').count()
    
    return {
        "total_users": total_users,
        "common_users": common_users,
        "admin_users": admin_users
    }