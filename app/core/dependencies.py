from fastapi import Depends, HTTPException, status
from .security import get_current_active_user, get_current_active_admin_user
from ..models.user_model import User

# Dependencias para usuarios normales (tokens normales)
def get_current_client_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es COMMON (cliente)
    Solo funciona con tokens de usuario normal
    """
    if current_user.user_type != 'common':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol CLIENT."
        )
    return current_user

# Dependencias para administradores (usan tokens admin)
def get_current_admin_user(
    current_user: User = Depends(get_current_active_admin_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es ADMIN
    Solo funciona con tokens admin
    """
    if current_user.user_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol ADMIN."
        )
    return current_user

def get_current_store_staff_user(
    current_user: User = Depends(get_current_active_admin_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es STORE_STAFF
    Solo funciona con tokens admin
    """
    if current_user.user_type != 'store_staff':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol STORE_STAFF."
        )
    return current_user

def get_current_admin_or_staff_user(
    current_user: User = Depends(get_current_active_admin_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es ADMIN o STORE_STAFF
    Solo funciona con tokens admin
    """
    if current_user.user_type not in ['admin', 'store_staff']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol ADMIN o STORE_STAFF."
        )
    return current_user