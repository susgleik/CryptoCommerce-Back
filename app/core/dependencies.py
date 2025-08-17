from fastapi import Depends, HTTPException, status
from .security import get_current_active_user
from ..models.user_model import User, UserRole

def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es ADMIN
    """
    if current_user.user_type != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol ADMIN."
        )
    return current_user

def get_current_store_staff_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es STORE_STAFF
    """
    if current_user.user_type != UserRole.STORE_STAFF.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol STORE_STAFF."
        )
    return current_user

def get_current_admin_or_staff_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es ADMIN o STORE_STAFF
    """
    if current_user.user_type not in [UserRole.ADMIN.value, UserRole.STORE_STAFF.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol ADMIN o STORE_STAFF."
        )
    return current_user

def get_current_client_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es COMMON (cliente)
    """
    if current_user.user_type != UserRole.COMMON.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol CLIENT."
        )
    return current_user
