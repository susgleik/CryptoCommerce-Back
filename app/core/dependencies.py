from fastapi import Depends, HTTPException, status
from .security import get_current_active_user
from ..models.user_model import User, UserRole

def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es ADMIN
    """
    print(f"Checking admin permissions for: {current_user.email}, type: {current_user.user_type}")
    
    if current_user.user_type != UserRole.ADMIN:
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
    if current_user.user_type != UserRole.STORE_STAFF:
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
    print(f"Checking admin/staff permissions for: {current_user.email}")
    print(f"User type: '{current_user.user_type}' (type: {type(current_user.user_type)})")
    print(f"UserRole.ADMIN: '{UserRole.ADMIN}' (type: {type(UserRole.ADMIN)})")
    print(f"UserRole.STORE_STAFF: '{UserRole.STORE_STAFF}' (type: {type(UserRole.STORE_STAFF)})")
    
    # Usar comparación de strings directa para evitar problemas
    if current_user.user_type not in ['admin', 'store_staff']:
        print(f"Access denied for user type: {current_user.user_type}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol ADMIN o STORE_STAFF."
        )
    
    print(f"Access granted for user: {current_user.email}")
    return current_user

def get_current_client_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependencia para verificar que el usuario actual es COMMON (cliente)
    """
    if current_user.user_type != UserRole.COMMON:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol CLIENT."
        )
    return current_user