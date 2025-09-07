from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
from ...database.database import get_db
from ...models.user_model import User
from ...schemas import user_schemas
from ...core.jwt_handler import create_admin_access_token, verify_password
from datetime import datetime, timezone
from ...core.dependencies import get_current_admin_or_staff_user

router = APIRouter(prefix="/admin")

@router.post(
    "/login",
    response_model=user_schemas.AdminTokenResponse,
    description="Login exclusivo para administradores y staff",
    status_code=status.HTTP_200_OK
)
def admin_login(
    form_data: user_schemas.UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == form_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Verificar contraseña
        if not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verificar que el usuario sea ADMIN o STORE_STAFF
        if user.user_type not in ['admin', 'store_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Se requieren permisos de administrador."
            )
        
        # Verificar que esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo"
            )
        
        # Actualizar última fecha de login
        try:
            user.last_login = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            print(f"Warning: Failed to update last_login for admin user {user.email}: {str(e)}")
        
        # Crear token admin con información adicional
        # CORREGIDO: usar user.user_id en lugar de user.id
        token_data = {
            "sub": user.email,
            "user_id": user.user_id,  # CAMBIO: user.id -> user.user_id
            "user_type": user.user_type,
            "role": user.user_type
        }
        
        access_token = create_admin_access_token(data=token_data)
        
        # CORREGIDO: Usar el objeto user directamente para que Pydantic haga el mapeo
        # En lugar de crear un dict manual, dejar que el schema AdminUserInfo maneje el mapeo
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,  # CAMBIO: Pasar el objeto user directamente
            "permissions": get_user_permissions(user.user_type)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
        
def get_user_permissions(user_type: str) -> list:
    """
    Retorna los permisos según el tipo de usuario
    """
    permissions_map = {
        'admin': [
            'manage_users',
            'manage_books',
            'view_reports',
            'manage_orders',
            'manage_inventory',
            'system_settings'
        ],
        'store_staff': [
            'manage_books',
            'manage_orders',
            'manage_inventory',
            'view_reports'
        ]
    }
    return permissions_map.get(user_type, [])

@router.post("/verify-token")
def verify_admin_token_endpoint(
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Verificar que el token admin es válido
    """
    return {
        "valid": True,
        "user": current_user,  # CAMBIO: Pasar el objeto user directamente
        "permissions": get_user_permissions(current_user.user_type)
    }